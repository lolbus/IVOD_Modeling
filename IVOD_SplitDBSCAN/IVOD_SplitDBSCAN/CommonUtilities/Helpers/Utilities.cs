using Newtonsoft.Json.Linq;
using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Drawing;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing.Imaging;
using System.Collections.Generic;
using System.Net;
using System.Linq;
using Microsoft.Net.Http.Headers;
using Microsoft.AspNetCore.WebUtilities;
using Newtonsoft.Json;

namespace CommonUtilities.Helpers
{
    public class Utilities
    {
        [DllImport("user32.dll", SetLastError = true)]
        public static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("kernel32.dll", EntryPoint = "RtlCopyMemory", SetLastError = false)]
        public static extern void CopyMemory(IntPtr dest, IntPtr src, uint count);

        private static object token = new object();

        public static Color StringToColor(string colorStr)
        {
            TypeConverter cc = TypeDescriptor.GetConverter(typeof(Color));
            var result = (Color)cc.ConvertFromString(colorStr);
            return result;
        }

        public static T GetConfigurationWithPath<T>(string Path, string attribute, T defaultvalue, string filePath)
        {
            try
            {
                var jsn = LoadJsonConfigurationFile(filePath);
                var tkn = jsn.SelectToken(Path);

                if (tkn != null)
                {

                    if (!string.IsNullOrEmpty(attribute))
                    {
                        if ((tkn[attribute] ?? null) != null)
                        {
                            var retVal = (T)Convert.ChangeType(tkn[attribute], typeof(T));
                            return retVal;
                        }
                        else
                        {
                            var retVal = (T)Convert.ChangeType(tkn, typeof(T));
                            return retVal;
                        }
                    }
                    else
                    {
                        T retVal;
                        if ("JTOKEN JOBJECT JARRAY".Contains(typeof(T).Name.ToUpper()))
                        {
                            retVal = (T)JsonConvert.DeserializeObject(tkn.ToString(), typeof(T));

                        }
                        else
                        {
                            retVal = (T)Convert.ChangeType(tkn, typeof(T));
                        }

                        return retVal;
                    }

                    //if (string.IsNullOrEmpty(attribute))
                    //{
                    //    T retVal = (T)Convert.ChangeType(tkn, typeof(T));
                    //    return retVal;
                    //}

                    //jsn = tkn as JObject;
                    //if (jsn[attribute] != null)
                    //{
                    //    T retVal = (T)Convert.ChangeType(jsn[attribute], typeof(T));
                    //    return retVal;
                    //}
                }
            }
            catch (Exception)
            {
                throw;
            }
            return defaultvalue;
        }

        public static JObject LoadJsonConfigurationFile(string path)
        {
            JObject jsn = new();
            try
            {
                if (!File.Exists($"{path}")) return jsn;
                using (StreamReader file = File.OpenText($"{path}"))
                {
                    jsn = JObject.Parse(file.ReadToEnd());
                }
            }
            catch (Exception)
            {
                throw;
            }
            return jsn;
        }

        public static async Task<string> SendToRestService_Task(string url, JObject data, string uid = "", string pwd = "", int timeout_ms = 100000)
        {
            string sretval = "";
            try
            {
                var base64EncodedAuthenticationString = "";
                var httpClient = new HttpClient();
                httpClient.Timeout = TimeSpan.FromMilliseconds(timeout_ms);
                if (uid.Trim() != "" && pwd.Trim() != "")
                {
                    var authenticationString = $"{uid}:{pwd}";
                    base64EncodedAuthenticationString = Convert.ToBase64String(ASCIIEncoding.UTF8.GetBytes(authenticationString));
                }

                HttpContent content = new StringContent("");

                if (data != null)
                    content = new StringContent(JObject.FromObject(data).ToString(), Encoding.UTF8, "application/json");

                if (base64EncodedAuthenticationString.Trim() != "")
                    httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Basic", base64EncodedAuthenticationString);

                HttpResponseMessage httpResMsg = await httpClient.PostAsync(url, content);
                if (httpResMsg.StatusCode == System.Net.HttpStatusCode.OK)
                {
                    sretval = await httpResMsg.Content.ReadAsStringAsync();
                }
                Debug.WriteLine($"url = {url}, httpResMsg.StatusCode = {httpResMsg.StatusCode}");
            }
            catch (Exception)
            {
                //throw;
            }
            return sretval;
        }

        public static async Task<(HttpStatusCode, string)> RestCallAsync(string url, HttpMethod httpMethod, string payload = "", double timeout = 10000)
        {
            var responseCode = HttpStatusCode.NotFound;
            var responseMsg = string.Empty;
            try
            {
                using (var client = new HttpClient())
                {
                    client.Timeout = TimeSpan.FromSeconds(timeout / 1000);
                    HttpRequestMessage request = new HttpRequestMessage
                    {
                        Method = httpMethod,
                        RequestUri = new Uri(url),
                    };

                    if (!string.IsNullOrEmpty(payload))
                    {
                        HttpContent c = new StringContent(payload, Encoding.UTF8, "application/json");
                        request.Content = c;
                    }

                    HttpResponseMessage result = await client.SendAsync(request);
                    if (result.IsSuccessStatusCode)
                    {
                        responseCode = result.StatusCode;
                        using (HttpContent content = result.Content)
                        {
                            responseMsg = await content.ReadAsStringAsync().ConfigureAwait(false);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                CommonHelper.DisplayConsole($"RestCallAsync exception: {ex.Message}");
            }
            return (responseCode, responseMsg);
        }

        public static HttpMethod GetHttpMethod(string method)
        {
            try
            {
                return new HttpMethod(method);
            }
            catch (Exception ex)
            {
                CommonHelper.DisplayConsole($"GetHttpMethod exception: {ex.Message}");
            }
            return HttpMethod.Get;
        }

        public static async Task<string> GetStreamAsync(string url)
        {
            try
            {
                using (HttpClient client = new HttpClient())
                {
                    using (Stream stream = await client.GetStreamAsync(url))
                    {
                        using (MemoryStream memoryStream = new MemoryStream())
                        {
                            byte[] buffer = new byte[8192];
                            int bytesRead;
                            while ((bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length)) > 0)
                            {
                                await memoryStream.WriteAsync(buffer, 0, bytesRead);
                            }
                            byte[] bytes = memoryStream.ToArray();

                            // Save the byte array as an image file
                            File.WriteAllBytes("image.jpg", bytes);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                var b = ex;
            }
            return "";
        }

        public static Bitmap ResizeImage(Bitmap bmpImage, int newDPI)
        {
            try
            {
                if (bmpImage == null) return null;
                Bitmap bmpResult = null;
                double origDPI = bmpImage.VerticalResolution;
                double newWidth = bmpImage.Width / origDPI * newDPI;
                double newHeight = bmpImage.Height / origDPI * newDPI;

                Bitmap bm_source = new(bmpImage);
                Size fitsize = FitImage(bmpImage.Size, (int)newWidth, (int)newHeight);
                Bitmap bm_dest = new(fitsize.Width, fitsize.Height);
                Graphics gr_dest = Graphics.FromImage(bm_dest);
                gr_dest.DrawImage(bm_source, 0, 0, bm_dest.Width + 1, bm_dest.Height + 1);

                Bitmap newImage = bm_dest;
                newImage.SetResolution(newDPI, newDPI);
                bmpResult = newImage;

                return bmpResult;
            }
            catch (Exception)
            {
                throw;
            }
        }

        public static Bitmap ResizeImage(Bitmap bmpImage, int newDPI, int width, int height)
        {
            try
            {
                if (bmpImage == null) return null;
                Bitmap bmpResult = null;
                double newWidth = width;
                double newHeight = height;

                Bitmap bm_source = new(bmpImage);
                Size fitsize = FitImage(bmpImage.Size, (int)newWidth, (int)newHeight);
                Bitmap bm_dest = new(fitsize.Width, fitsize.Height);
                Graphics gr_dest = Graphics.FromImage(bm_dest);
                gr_dest.DrawImage(bm_source, 0, 0, bm_dest.Width + 1, bm_dest.Height + 1);

                Bitmap newImage = bm_dest;
                newImage.SetResolution(newDPI, newDPI);
                bmpResult = newImage;

                return bmpResult;
            }
            catch (Exception)
            {
                throw;
            }
        }

        private static Size FitImage(Size img, int _w, int _h)
        {
            Size box = new(0, 0);
            box.Width = _w;
            box.Height = _h;

            double boxRatio = (double)box.Width / (double)box.Height;//Lets say 400/500= 0.8 
            double imgRatio = (double)img.Width / (double)img.Height;//Lets say 1200/1000= 1.2 and 800/1200=.667
            double fixRatio = 0.0f;

            if (imgRatio > boxRatio)//Image is wider , Fix Width first case
            {
                fixRatio = (double)box.Width / (double)img.Width; //400/1200=0.33
            }
            else //Image is taller or equal, Fix Height
            {
                fixRatio = (double)box.Height / (double)img.Height;//500/1200=0.41666667
            }

            return new Size((int)(img.Width * fixRatio), (int)(img.Height * fixRatio)); //first case using .33=(400,333), Second Case using .41666667=(333,500);
        }

        private static Bitmap BitmapAdjustment(Bitmap originalImage, float brightness = 1.0f, float contrast = 1.0f, float gamma = 1.0f)
        {
            Bitmap adjustedImage = new Bitmap(originalImage.Width, originalImage.Height);

            float adjustedBrightness = brightness - 1.0f;
            // create matrix that will brighten and contrast the image
            float[][] ptsArray ={
                new float[] {contrast, 0, 0, 0, 0}, // scale red
                new float[] {0, contrast, 0, 0, 0}, // scale green
                new float[] {0, 0, contrast, 0, 0}, // scale blue
                new float[] {0, 0, 0, 1.0f, 0}, // don't scale alpha
                new float[] {adjustedBrightness, adjustedBrightness, adjustedBrightness, 0, 1}
            };

            ImageAttributes imageAttributes = new ImageAttributes();
            imageAttributes.ClearColorMatrix();
            imageAttributes.SetColorMatrix(new ColorMatrix(ptsArray), ColorMatrixFlag.Default, ColorAdjustType.Bitmap);
            imageAttributes.SetGamma(gamma, ColorAdjustType.Bitmap);
            Graphics g = Graphics.FromImage(adjustedImage);
            g.DrawImage(originalImage, new Rectangle(0, 0, adjustedImage.Width, adjustedImage.Height)
                , 0, 0, originalImage.Width, originalImage.Height,
                GraphicsUnit.Pixel, imageAttributes);

            return adjustedImage;
        }

        public static bool IsValidJson(string json)
        {
            try
            {
                JToken.Parse(json);
                return true;
            }
            catch (Newtonsoft.Json.JsonReaderException)
            {
                //Trace.WriteLine(ex);
                return false;
            }
        }
        public static T Create_Instance<T>(string asmfile, string asmtype)
        {
            T ipl = default;
            try
            {
                var asm = Assembly.LoadFile(asmfile);
                if (asm != null)
                {
                    try
                    {
                        Type[] tps = asm.GetTypes();
                        Type tp = asm.GetType(asmtype);
                        ipl = (T)Activator.CreateInstance(tp);
                    }
                    catch (ReflectionTypeLoadException ex)
                    {
                        // now look at ex.LoaderExceptions - this is an Exception[], so:
                        foreach (Exception inner in ex.LoaderExceptions)
                        {
                            // write details of "inner", in particular inner.Message
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                throw;
            }
            return ipl;
        }

        public static T CreateLateBindInstance<T>(string tokenPathDll, string tokenPathType)
        {
            if (!string.IsNullOrEmpty(tokenPathDll))
            {
                string asmfile = $"{tokenPathDll}";
                if (!File.Exists(asmfile))
                    asmfile = $"{AppDomain.CurrentDomain.BaseDirectory}\\{tokenPathDll}";

                if (File.Exists(asmfile))
                {
                    string absolute = Path.GetFullPath(asmfile);
                    T lib = Create_Instance<T>(absolute, tokenPathType);
                    if (lib == null)
                    {
                        CommonHelper.LogData_Thread($"Failed to Instantiate CreateLateBindInstance: {typeof(T)}", 0, true);
                    }
                    else
                    {
                        return lib;
                    }
                }
                else
                {
                    CommonHelper.LogData_Thread($"CreateLateBindInstance Entry Assemblly file not found: {asmfile}", 0, true);
                }
            }
            return default;
        }

        #region image util
        public static Bitmap ConvertBase64ToBitmap(string content)
        {
            try
            {
                var bImg = Convert.FromBase64String(content);
                System.Drawing.Bitmap bmpVal = new System.Drawing.Bitmap(new System.IO.MemoryStream(bImg));
                return bmpVal;
            }
            catch (Exception ex)
            {
            }
            return null;
        }

        public static string ConvertBase64ImageToJpegBase64(string content, bool testSave = false, string saveFormat = "PNG", string fileprefix = "")
        {
            string sRetval = content;
            try
            {
                var bImg = Convert.FromBase64String(content);
                System.Drawing.Bitmap bmpVal = new System.Drawing.Bitmap(new System.IO.MemoryStream(bImg));
                sRetval = BitmapToBase64Sting(bmpVal, testSave);
                if (testSave)
                {
                    string sfolder = @".\CaptureResult\";
                    string folderPath = sfolder + fileprefix + "_" + DateTime.Now.ToString("yyyyMMddHHmmssffff");
                    if (!System.IO.Directory.Exists(sfolder)) System.IO.Directory.CreateDirectory(sfolder);
                    bmpVal.Save($"{folderPath}.{saveFormat}");
                }
            }
            catch (Exception ex)
            {
                sRetval = ConvertRawToBase64String(content, testSave, saveFormat, fileprefix);
            }
            return sRetval;
        }

        public static string ConvertRawToBase64String(string input, bool testSave = false, string saveFormat = "PNG", string fileprefix = "")
        {
            try
            {
                if (string.IsNullOrEmpty(input)) return input;
                var data = Convert.FromBase64String(input);
                IntPtr unmanagedPtr = Marshal.AllocHGlobal(data.Length);
                Marshal.Copy(data, 0, unmanagedPtr, data.Length);
                IntPtr buffer = unmanagedPtr;
                lock (token)
                {
                    int width = 640;
                    int height = 480;
                    int bytes = width * height;

                    var bmp = new System.Drawing.Bitmap(width, height, System.Drawing.Imaging.PixelFormat.Format8bppIndexed);
                    System.Drawing.Rectangle rect = new System.Drawing.Rectangle(0, 0, bmp.Width, bmp.Height);
                    var bmpData = bmp.LockBits(rect, System.Drawing.Imaging.ImageLockMode.ReadWrite, bmp.PixelFormat);

                    System.Drawing.Imaging.ColorPalette tempPalette;
                    tempPalette = bmp.Palette;

                    for (int i = 0; i < 256; i++)
                    {
                        tempPalette.Entries[i] = System.Drawing.Color.FromArgb(i, i, i);
                    }

                    bmp.Palette = tempPalette;

                    CopyMemory(bmpData.Scan0, buffer, (uint)bytes);
                    bmp.UnlockBits(bmpData);

                    System.Drawing.Bitmap resized = bmp.Clone() as System.Drawing.Bitmap;
                    if (testSave)
                    {
                        string folderPath = @".\CaptureResult\" + fileprefix + "_" + DateTime.Now.ToString("yyyyMMddHHmmssffff");
                        resized.Save($"{folderPath}.{saveFormat}");
                    }
                    return BitmapToBase64Sting(resized);
                }
            }
            catch (Exception ex)
            {
                return "";
            }
        }

        public static string ConvertRawToBase64String(byte[] data)
        {
            IntPtr unmanagedPtr = Marshal.AllocHGlobal(data.Length);
            Marshal.Copy(data, 0, unmanagedPtr, data.Length);
            IntPtr buffer = unmanagedPtr;
            lock (token)
            {
                int width = 640;
                int height = 480;
                int bytes = width * height;

                var bmp = new Bitmap(width, height, System.Drawing.Imaging.PixelFormat.Format8bppIndexed);
                System.Drawing.Rectangle rect = new System.Drawing.Rectangle(0, 0, bmp.Width, bmp.Height);
                var bmpData = bmp.LockBits(rect, ImageLockMode.ReadWrite, bmp.PixelFormat);

                ColorPalette tempPalette;
                tempPalette = bmp.Palette;

                for (int i = 0; i < 256; i++)
                {
                    tempPalette.Entries[i] = System.Drawing.Color.FromArgb(i, i, i);
                }

                bmp.Palette = tempPalette;

                CopyMemory(bmpData.Scan0, buffer, (uint)bytes);
                bmp.UnlockBits(bmpData);

                Bitmap resized = bmp.Clone() as Bitmap;
                return BitmapToBase64Sting(resized);
            }
        }

        public static Bitmap WriteBitmapFile(int width, int height, byte[] imageData)
        {
            byte[] newData = new byte[imageData.Length];

            //for (int x = 0; x < imageData.Length; x += 4)
            //{
            //    byte[] pixel = new byte[4];
            //    Array.Copy(imageData, x, pixel, 0, 4);

            //    byte r = pixel[0];
            //    byte g = pixel[1];
            //    byte b = pixel[2];
            //    byte a = pixel[3];

            //    byte[] newPixel = new byte[] { b, g, r, a };

            //    Array.Copy(newPixel, 0, newData, x, 4);
            //}

            //imageData = newData;

            using (var stream = new MemoryStream(imageData))
            using (var bmp = new Bitmap(width, height, PixelFormat.Format24bppRgb))
            {
                BitmapData bmpData = bmp.LockBits(new Rectangle(0, 0, bmp.Width, bmp.Height), ImageLockMode.WriteOnly, bmp.PixelFormat);

                IntPtr pNative = bmpData.Scan0;
                Marshal.Copy(imageData, 0, pNative, imageData.Length);

                bmp.UnlockBits(bmpData);
                return bmp;
            }
        }

        public static string BitmapToBase64Sting(Bitmap bmpImage, bool testSave = false)
        {
            string sRetval = "";
            try
            {
                if (bmpImage != null)
                {
                    System.Drawing.ImageConverter converter = new System.Drawing.ImageConverter();
                    sRetval = Convert.ToBase64String((byte[])converter.ConvertTo(bmpImage, typeof(byte[]))); //Get Base64
                }
            }
            catch (Exception ex)
            {
                //logger.Error(ex, MethodBase.GetCurrentMethod().DeclaringType.Name);
            }
            return sRetval;
        }

        public static System.Drawing.Bitmap resizeImage(System.Drawing.Image imgToResize, System.Drawing.Size size)
        {
            //Get the image current width  
            int sourceWidth = imgToResize.Width;
            //Get the image current height  
            int sourceHeight = imgToResize.Height;
            float nPercent = 0;
            float nPercentW = 0;
            float nPercentH = 0;
            //Calulate  width with new desired size  
            nPercentW = ((float)size.Width / (float)sourceWidth);
            //Calculate height with new desired size  
            nPercentH = ((float)size.Height / (float)sourceHeight);
            if (nPercentH < nPercentW)
                nPercent = nPercentH;
            else
                nPercent = nPercentW;
            //New Width  
            int destWidth = (int)(sourceWidth * nPercentW);
            //New Height  
            int destHeight = (int)(sourceHeight * nPercentH);
            System.Drawing.Bitmap b = new System.Drawing.Bitmap(destWidth, destHeight);
            System.Drawing.Graphics g = System.Drawing.Graphics.FromImage(b);
            g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
            // Draw image with new width and height  
            g.DrawImage(imgToResize, 0, 0, destWidth, destHeight);
            g.Dispose();
            return b;
        }

        public static System.Drawing.Bitmap MakeGrayscale3(System.Drawing.Bitmap original)
        {
            //create a blank bitmap the same size as original
            System.Drawing.Bitmap newBitmap = new System.Drawing.Bitmap(original.Width, original.Height);

            //get a graphics object from the new image
            using (System.Drawing.Graphics g = System.Drawing.Graphics.FromImage(newBitmap))
            {
                //create the grayscale ColorMatrix
                System.Drawing.Imaging.ColorMatrix colorMatrix = new System.Drawing.Imaging.ColorMatrix(
                   new float[][]
                   {
                     new float[] {.3f, .3f, .3f, 0, 0},
                     new float[] {.59f, .59f, .59f, 0, 0},
                     new float[] {.11f, .11f, .11f, 0, 0},
                     new float[] {0, 0, 0, 1, 0},
                     new float[] {0, 0, 0, 0, 1}
                   });

                //create some image attributes
                using (System.Drawing.Imaging.ImageAttributes attributes = new System.Drawing.Imaging.ImageAttributes())
                {

                    //set the color matrix attribute
                    attributes.SetColorMatrix(colorMatrix);

                    //draw the original image on the new image
                    //using the grayscale color matrix
                    g.DrawImage(original, new System.Drawing.Rectangle(0, 0, original.Width, original.Height),
                                0, 0, original.Width, original.Height, System.Drawing.GraphicsUnit.Pixel, attributes);
                }
            }
            return newBitmap;
        }

        public static string ConvertWsqFileToBase64(string file)
        {
            Byte[] bytes = File.ReadAllBytes(file);
            string base64String = Convert.ToBase64String(bytes, 0, bytes.Length);
            return base64String;
        }
        #endregion image util

        #region 32bit dll handling
        public static void Process32BitDllHandling(string filename, string cmd)
        {
            // Use ProcessStartInfo class
            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.CreateNoWindow = false;
            startInfo.UseShellExecute = false;
            startInfo.FileName = filename;
            startInfo.WindowStyle = ProcessWindowStyle.Hidden;
            if (!string.IsNullOrEmpty(cmd))
                startInfo.Arguments = cmd;

            try
            {
                // Start the process with the info we specified.
                // Call WaitForExit and then the using statement will close.
                using (Process exeProcess = Process.Start(startInfo))
                {
                    exeProcess.WaitForExit();
                }
            }
            catch (Exception ex)
            {
                // Log error.
                CommonHelper.DisplayConsole($"Process32BitDllHandling exception: {ex}");
            }
        }
        #endregion 32bit dll handling
    }
}
