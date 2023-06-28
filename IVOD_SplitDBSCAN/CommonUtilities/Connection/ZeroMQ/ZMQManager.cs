using CommonUtilities.Helpers;
using NetMQ;
using NetMQ.Sockets;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;

namespace CommonUtilities.Connection.ZeroMQ
{
    public static class ZMQManager
    {
        //private static PublisherSocket pubGenSocket = null;
        private static Dictionary<string, PublisherSocket> pubGenSockets = new();
        private static bool _bStart = false;
        public static bool StartZeroMQSubscriber(string address, string[] topic, System.EventHandler messageCallBack)
        {
            try
            {

                _bStart = true;
                if (!string.IsNullOrEmpty(address))
                {
                    Task.Run(() =>
                    {
                        try
                        {
                            using (var subSocket = new SubscriberSocket())
                            {
                                subSocket.Options.ReceiveHighWatermark = 10000;
                                if (address.IndexOf(@"//*") >= 0)
                                {
                                    if (!_bStart)
                                        subSocket.Bind(address);
                                }
                                else
                                {
                                    subSocket.Connect(address);
                                }

                                if (topic != null)
                                {
                                    if (topic.Length > 0)
                                    {
                                        CommonHelper.DisplayConsole($"Subscriber Topic : {string.Join(", ", topic)}");
                                        foreach (var t in topic)
                                        {
                                            string s = (string)t;
                                            if (!string.IsNullOrEmpty(s))
                                            {
                                                subSocket.Subscribe(s);
                                            }
                                        }
                                    }
                                    else
                                    {
                                        CommonHelper.DisplayConsole($"Subscriber Topic : All");
                                        subSocket.Subscribe("");
                                    }
                                }
                                else
                                {
                                    CommonHelper.DisplayConsole($"Subscriber Topic : All");
                                    subSocket.Subscribe("");
                                }

                                while (_bStart)
                                {
                                    string messageTopicReceived = subSocket.ReceiveFrameString();
                                    string messageReceived = subSocket.ReceiveFrameString();

                                    string msgrec = $"Message received from Topic : {messageTopicReceived}";
                                    dynamic qMsg = new JObject();
                                    qMsg.message = messageReceived;
                                    qMsg.topic = messageTopicReceived;

                                    messageCallBack?.Invoke(qMsg, null);
                                    System.Threading.Thread.Sleep(5);
                                }
                                subSocket.Close();
                            }
                        }
                        catch (Exception ex)
                        {
                            CommonHelper.LogData_Thread($"StartZeroMQSubscriber Exception {ex.ToString()}", 2);
                        }
                    });
                }
            }
            catch (Exception ex)
            {
                CommonHelper.LogData_Thread($"StartZeroMQSubscriber Exception {ex.ToString()}", 2);
            }
            return _bStart;
        }


        public static bool StopZeroMQSubscriber()
        {
            try
            {
                _bStart = false;

            }
            catch (Exception ex)
            {
                CommonHelper.LogData_Thread($"StopZeroMQSubscriber Exception {ex.ToString()}", 2);
            }
            return _bStart;
        }

        public static bool Publish_General_ZeroMQ(string topic, dynamic msg, string address)
        {
            bool bretval = false;
            int delay = 300;
            string clsname = "";
            string MethodName = CommonHelper.GetCurrentMethodName(MethodBase.GetCurrentMethod(), ref clsname);
            int logtype = 8;
            try
            {
                string mth = $"{clsname}.{MethodName}";
                string logmsg = $"{mth} ---------Start------";
                CommonHelper.LogData_Thread(logmsg, logtype);
                if (!string.IsNullOrEmpty(address))
                {
                    string hashAddr = CommonHelper.ComputeSha256Hash(address);
                    if (!pubGenSockets.TryGetValue(hashAddr, out PublisherSocket pubGenSocket))
                    {
                        logmsg = $"{mth} :Initialing ZeroMQ Publisher";
                        CommonHelper.LogData_Thread(logmsg, logtype);
                        pubGenSocket = new PublisherSocket();
                        pubGenSocket.Options.ReceiveHighWatermark = 1000;
                        if (address.IndexOf(@"//*") >= 0)
                            pubGenSocket.Bind(address);
                        else
                            pubGenSocket.Connect(address);

                        logmsg = $"{mth} :Connected to ZeroMQ service";
                        CommonHelper.LogData_Thread(logmsg, logtype);
                        System.Threading.Thread.Sleep(delay);

                        pubGenSockets.Add(hashAddr, pubGenSocket);
                    }

                    logmsg = $"{mth} : Sending Message to ZeroMQ Service";
                    CommonHelper.LogData_Thread(logmsg, logtype);
                    string sMsg = Convert.ToString(msg);
                    pubGenSocket?.SendMoreFrame(topic).SendFrame(sMsg);
                    logmsg = $"{mth} : Sent Message to ZeroMQ Service. topic : {topic}";
                    CommonHelper.LogData_Thread(logmsg, logtype);
                }
            }
            catch (Exception)
            {
            }
            return bretval;
        }
    }
}
