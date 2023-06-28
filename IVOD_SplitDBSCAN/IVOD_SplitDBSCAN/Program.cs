using CommonUtilities.Helpers;
using Newtonsoft.Json.Linq;
using CommonUtilities.Classes;
using CommonUtilities.Connection.ZeroMQ;
using Dbscan;

namespace IVOD_SplitDBSCAN
{
    public class Vector
    {
        public double X { get; set; }
        public double Y { get; set; }
        public double Z { get; set; }
    }

    public class PointData : IPointData
    {
        public double X { get; set; }
        public double Y { get; set; }

        public Point Point => new Point(X, Y);
    }

    public class Limits
    {
        public double lowR { get; set; }
        public double upR { get; set; }
        public double lowA { get; set; }
        public double upA { get; set; }
        public double lowE { get; set; }
        public double upE { get; set; }
    }

    public class Program
    {
        #region Public Variables
        private static List<Vector> _tmp = new List<Vector>() { };
        public static List<Vector> Tmp
        {
            get { return _tmp; }
            set { _tmp = value; }
        }

        private static List<List<Vector>> _rawData = new List<List<Vector>>() { };
        public static List<List<Vector>> RawData
        {
            get { return _rawData; }
            set { _rawData = value; }
        }

        private static DateTime _startTime = DateTime.Now;
        public static DateTime StartTime
        {
            get { return _startTime; }
            set { _startTime = value; }
        }

        private static List<Vector> _centroids = new List<Vector>() { };
        public static List<Vector> Centroids
        {
            get { return _centroids; }
            set { _centroids = value; }
        }

        private static bool _receivedData = false;
        public static bool ReceivedData
        {
            get { return _receivedData; }
            set { _receivedData = value; }
        }
        #endregion Public Variables

        #region Fixed Variables
        private static JObject zPub = Utilities.GetConfigurationWithPath("zeromq", "publisher", new JObject(), Constants.GeneralConfig);
        private static JObject zSub = Utilities.GetConfigurationWithPath("zeromq", "subscriber", new JObject(), Constants.GeneralConfig);
        private static Limits Limit = Utilities.GetConfigurationWithPath("pointLimit", "", new JObject(), Constants.GeneralConfig).ToObject<Limits>();
        private static JObject DBSCANparams = Utilities.GetConfigurationWithPath("dbscanParams", "", new JObject(), Constants.GeneralConfig);
        private static EventHandler zmqReceiveHandler;
        private static CancellationTokenSource _RawCts;
        private static CancellationTokenSource _CentCts;
        #endregion Fixed Variables

        private static void zmqReceiveMessage(object sender, EventArgs args)
        {
            if (sender != null)
            {
                try
                {
                    JObject jObjSender = JObject.FromObject(sender);
                    if (!jObjSender.IsNullOrEmpty() && !jObjSender["message"].IsNullOrEmpty())
                    {
                        string msg = jObjSender.Value<string>("message");
                        JObject message = JObject.Parse(msg.Replace("radar_data ", ""));
                        try
                        {
                            if (jObjSender["topic"].ToString() == zSub["topic"].ToString() || message["topic"].ToString() == zSub["topic"].ToString())
                            {
                                JArray packet = message["packets"][0]["data"].ToObject<JArray>();
                                if (packet != null)
                                {
                                    foreach (JObject p in packet)
                                    {
                                        if (p["x"] != null)
                                        {
                                            Tmp.Add(new Vector { X = p["x"].Value<double>(), Y = p["y"].Value<double>(), Z = p["z"].Value<double>() });
                                        }
                                    }

                                    if (DateTime.Now.Subtract(StartTime).TotalMilliseconds >= 500)
                                    {
                                        RawData.Add(new List<Vector>(Tmp));
                                        Tmp.Clear();
                                        StartTime = DateTime.Now;
                                        if (RawData.Count > 10)
                                        {
                                            RawData.RemoveAt(0);
                                        }
                                        ReceivedData = true;
                                    }
                                }
                            }
                        }
                        catch { }
                    }
                }
                catch { }
            }
        }
        
        public static PointData ClusterRaw(List<PointData> data)
        {
            var clusters = Dbscan.Dbscan.CalculateClusters<PointData>(
                data,
                epsilon: float.Parse(DBSCANparams["rawEps"].ToString()),
                minimumPointsPerCluster: int.Parse(DBSCANparams["rawMin"].ToString()));
            double avgX = 0;
            double avgY = 0;
            int index = 0;
            foreach (Cluster<PointData> c in clusters.Clusters)
            {
                foreach (PointData o in c.Objects)
                {
                    avgX += o.X;
                    avgY += o.Y;
                    index++;
                }
            }
            PointData centroid = new PointData { X = avgX / index, Y = avgY / index };
            return centroid;
        }

        public static async Task RawDataClustering(CancellationToken cancellationToken)
        {
            while (true)
            {
                try
                {
                    DateTime start_time = DateTime.Now;
                    List<List<Vector>> WorkingData = new List<List<Vector>>(RawData);
                    JArray jVectArr = new JArray();

                    for (double r = Limit.lowR + (Limit.upR - Limit.lowR) / 15; r <= Limit.upR; r += (Limit.upR - Limit.lowR) / 15)
                    {
                        double upSegR = r;
                        double lowSegR = r - ((Limit.upR - Limit.lowR) / 15);
                        for (double a = Limit.lowA + (Limit.upA - Limit.lowA) / 16; a <= Limit.upA; a += (Limit.upA - Limit.lowA) / 16)
                        {
                            double upSegA = a;
                            double lowSegA = a - ((Limit.upA - Limit.lowA) / 16);
                            for (double e = Limit.lowE + ((Limit.upE - Limit.lowE) / 8); e <= Limit.upE; e += (Limit.upE - Limit.lowE) / 8)
                            {
                                List<PointData> DataCube = new List<PointData>() { };
                                double upSegE = e;
                                double lowSegE = e - ((Limit.upE - Limit.lowE) / 8);
                                foreach (List<Vector> w in WorkingData)
                                {
                                    if (w != null)
                                    {
                                        foreach (Vector v in w)
                                        {
                                            if (lowSegR < v.Y && v.Y < upSegR && lowSegA < v.X && v.X < upSegA && lowSegE < v.Z && v.Z < upSegE)
                                            {
                                                DataCube.Add(new PointData { X = v.X, Y = v.Y });
                                            }
                                        }
                                    }
                                }
                                if (DataCube.Count > 0)
                                {
                                    PointData Centroid = ClusterRaw(DataCube);
                                    if (!double.IsNaN(Centroid.X))
                                    {
                                        Centroids.Add(new Vector() { X = Centroid.X, Y = Centroid.Y, Z = (upSegE + lowSegE) / 2 });
                                        JObject jVectObj = new JObject();
                                        jVectObj["x"] = Centroid.X;
                                        jVectObj["y"] = Centroid.Y;
                                        jVectObj["z"] = (upSegE + lowSegE) / 2;
                                        jVectArr.Add(jVectObj);
                                    }
                                }
                            }
                        }
                    }
                    JObject resultObj = new JObject();
                    resultObj["dataName"] = "Centroids";
                    resultObj["package"] = jVectArr;
                    try
                    {
                        ZMQManager.Publish_General_ZeroMQ(zPub["topic"].ToString(), resultObj, zPub["url"].ToString());

                        Console.WriteLine($"Number of centroids: {Centroids.Count}");
                    }
                    catch 
                    {
                        Console.WriteLine("Failed to send Centroids");
                    }
                    while (DateTime.Now.Subtract(start_time).TotalMilliseconds <= 500) { }
                }
                catch (Exception e)
                {
                    Console.WriteLine(e);
                }
            }
        }
        
        public static async Task CentDataClustering(CancellationToken cancellationToken)
        {
            while (true)
            {
                try
                {
                    DateTime start_time = DateTime.Now;
                    List<PointData> CentVec = new List<PointData>() { };
                    foreach (Vector c in Centroids)
                    {
                        if (c == null) continue;
                        CentVec.Add(new PointData { X = c.X, Y = c.Y });
                    }
                    Centroids.Clear();
                    var clusters = Dbscan.Dbscan.CalculateClusters<PointData>(
                    CentVec,
                    epsilon: float.Parse(DBSCANparams["centEps"].ToString()),
                    minimumPointsPerCluster: int.Parse(DBSCANparams["centMin"].ToString()));
                    List<PointData> PplLocale = new List<PointData>() { };
                    JArray jVectArr = new JArray();
                    for (int i = 0; i < clusters.Clusters.Count; i++)
                    {
                        double avgX = 0;
                        double avgY = 0;
                        int index = 0;
                        foreach (PointData o in clusters.Clusters[i].Objects)
                        {
                            avgX += o.X;
                            avgY += o.Y;
                            index++;
                        }
                        PplLocale.Add(new PointData { X = avgX / index, Y = avgY / index });
                        JObject jVectObj = new JObject();
                        jVectObj["x"] = avgX / index;
                        jVectObj["y"] = avgY / index;
                        jVectArr.Add(jVectObj);
                    }
                    JObject resultObj = new JObject();
                    resultObj["dataName"] = "People";
                    resultObj["package"] = jVectArr;
                    try
                    {
                        ZMQManager.Publish_General_ZeroMQ(zPub["topic"].ToString(), resultObj, zPub["url"].ToString());

                        Console.WriteLine($"Number of People: {PplLocale.Count}");
                    }
                    catch
                    {
                        Console.WriteLine("Failed to send people");
                    }
                    while (DateTime.Now.Subtract(start_time).TotalMilliseconds <= 500) ;
                }
                catch
                {
                    Console.WriteLine("No Person Dectected");
                }
            }
        }

        public static void StartRawCluster()
        {
            if (_RawCts != null)
            {
                return;
            }

            _RawCts = new CancellationTokenSource();
            Task.Run(() => RawDataClustering(_RawCts.Token));
        }
        
        public static void StartCentCluster()
        {
            if (_CentCts != null)
            {
                return;
            }

            _CentCts = new CancellationTokenSource();
            Task.Run(() => CentDataClustering(_CentCts.Token));
        }

        public static void Main(string[] args)
        {
            zmqReceiveHandler = zmqReceiveMessage;
            ZMQManager.StartZeroMQSubscriber(zSub["url"].ToString(), new string[] { zSub["topic"].ToString() }, zmqReceiveHandler);
            StartCentCluster();
            StartRawCluster();
            while (true)
            {
                DateTime start_time = DateTime.Now;
                while (DateTime.Now.Subtract(start_time).TotalMilliseconds <= 500) ;
                if (!ReceivedData)
                {
                    Centroids.Clear();
                    RawData.Clear();
                }
            }
        }
    }
}