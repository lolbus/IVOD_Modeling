using NetMQ.Sockets;
using NetMQ;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Newtonsoft.Json.Linq;
using Serilog;
using Serilog.Core;
using Serilog.Events;
using System.Threading.Tasks;
using System.Threading;
using System.Collections.ObjectModel;
using System.Globalization;
using System.Text.RegularExpressions;
using System.Security.Cryptography;
using System.Text;
using Microsoft.IdentityModel.Tokens;
using System.Diagnostics;

namespace CommonUtilities.Helpers
{
    public static class CommonHelper
    {
        public static ILogger logger;

        public static void LogData_Thread(string message, int type = 1, bool logConsole = false)
        {
            try
            {
                System.Threading.Thread t = new System.Threading.Thread(() =>
                {
                    LogMessage(message, type, logConsole);
                });
                t.Start();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"LogData_Thread exception: {ex.Message}");
            }
        }

        public static void ReadIniFileValue(string fileName, string k, out string v)
        {
            var dictionary = File.ReadLines(fileName).Select(s => s.Split('=')).Where(o => o.Length > 1).Select(s => new
            {
                key = s[0],
                value = string.Join("=", s.Select((o, n) => new
                {
                    n,
                    o
                }).Where(o => o.n > 0).Select(o => o.o))
            }).ToDictionary(o => o.key, o => o.value).TryGetValue(k.Trim(), out v);
        }

        public static string Between(string text, string from, string to)
        {
            string sretval = text;
            if (text.Contains(from, StringComparison.CurrentCulture) && text.IndexOf(to, text.IndexOf(from)) >= 0)
                sretval = text[(text.IndexOf(from) + from.Length)..text.IndexOf(to, text.IndexOf(from))];

            return sretval;
        }

        public static string GetCurrentMethodName(MethodBase mb, ref string classname)
        {
            string sRetval = mb.DeclaringType.Name;
            classname = "";
            try
            {
                if (sRetval.Contains("<") && sRetval.Contains(">"))
                {
                    sRetval = Between(mb.DeclaringType.Name, "<", ">");
                    classname = mb.ReflectedType.DeclaringType.FullName ?? "";
                }
                else
                {
                    sRetval = mb.Name;
                    classname = mb.DeclaringType.FullName ?? "";
                }
            }
            catch (Exception)
            { }

            return sRetval;
        }

        public static string GetCurrentMethodName()
        {
            // Get the current method's metadata.
            MethodBase method = System.Reflection.MethodBase.GetCurrentMethod();

            // Get the name of the current method.
            string methodName = method.Name;

            return methodName;
        }

        public static void CreateLogger(dynamic settings)
        {
            if (settings.levelswitch != null && settings.path != null)
            {
                ILogger _logger;
                Dictionary<string, LoggingLevelSwitch> levelSwitchDict = new() { };
                levelSwitchDict.Add("VERBOSE", new LoggingLevelSwitch(LogEventLevel.Verbose));
                levelSwitchDict.Add("DEBUG", new LoggingLevelSwitch(LogEventLevel.Debug));
                levelSwitchDict.Add("INFORMATION", new LoggingLevelSwitch(LogEventLevel.Information));
                levelSwitchDict.Add("ERROR", new LoggingLevelSwitch(LogEventLevel.Error));
                levelSwitchDict.Add("FATAL", new LoggingLevelSwitch(LogEventLevel.Fatal));

                // load log configuration
                var logtypename = $"{settings.levelswitch}";
                logtypename = logtypename.ToUpper().Trim();
                if (!levelSwitchDict.TryGetValue(logtypename, out LoggingLevelSwitch levelSwitch))
                    levelSwitch = new LoggingLevelSwitch(LogEventLevel.Information);

                string template = "{Timestamp:HH:mm:ss:fff} [{Level}] Message: {Message}{NewLine}{Properties}{NewLine}{Exception}";
                _logger = new LoggerConfiguration()
                    .Enrich.FromLogContext()
                    .MinimumLevel.ControlledBy(levelSwitch)
                    .WriteTo.Debug()
                    .WriteTo.File($"{settings.path}", rollingInterval: RollingInterval.Day, outputTemplate: template)
                    .CreateLogger();

                logger = _logger.ForContext("Source", $"{settings.source}") as Logger;
            }
        }

        public static void DisplayConsole(string Message)
        {
            try
            {
                Console.WriteLine($"{DateTime.Now:HH:mm:ss.fff} : {Message}");
            }
            catch (Exception ex)
            { }
        }

        public static async Task Run(Func<Task> action, Func<Exception, bool> errorHandler, TimeSpan retryDelay)
        {
            while (true)
            {
                try
                {
                    await action();
                    return;
                }
                catch (Exception ex)
                {
                    if (!errorHandler(ex))
                    {
                        return;
                    }
                }
                await Task.Delay(retryDelay);
            }
        }

        private static string ConvertJsonValue(object objValue)
        {
            string sRetval = "";
            try
            {
                if (objValue is System.Drawing.Bitmap or System.Drawing.Image)
                {
                    System.Drawing.Bitmap bmpVal = objValue as System.Drawing.Bitmap;
                    sRetval = bmpVal.ConvertBitmapToBase64String(System.Drawing.Imaging.ImageFormat.Jpeg);
                }
                else if (objValue is string or int)
                {
                    sRetval = objValue.ToString().Trim();
                }
            }
            catch (Exception)
            {
                throw;
            }
            return sRetval;
        }

        private static bool IsValidId(string id, string idType)
        {
            try
            {
                if ((idType != "O") && (string.IsNullOrEmpty(id) || id.Length != 9))
                    return false;

                switch (idType)
                {
                    case "N":
                    case "F":
                        id = id.ToUpper();

                        var icArray = id.ToCharArray();
                        var weight = 0;

                        weight += int.Parse(icArray[1].ToString()) * 2;
                        weight += int.Parse(icArray[2].ToString()) * 7;
                        weight += int.Parse(icArray[3].ToString()) * 6;
                        weight += int.Parse(icArray[4].ToString()) * 5;
                        weight += int.Parse(icArray[5].ToString()) * 4;
                        weight += int.Parse(icArray[6].ToString()) * 3;
                        weight += int.Parse(icArray[7].ToString()) * 2;

                        var offset = (icArray[0] == 'T' || icArray[0] == 'G') ? 4 : 0;
                        var temp = (offset + weight) % 11;

                        string[] st = new string[] { "J", "Z", "I", "H", "G", "F", "E", "D", "C", "B", "A" };
                        string[] fg = new string[] { "X", "W", "U", "T", "R", "Q", "P", "N", "M", "L", "K" };

                        //If prefix starts with S or T, suffix will be in st array; if prefix starts with F or G, suffix will be in fg array
                        var possibleSuffix = (icArray[0] == 'S' || icArray[0] == 'T') ? st[temp] : ((icArray[0] == 'F' || icArray[0] == 'G') ? fg[temp] : null);

                        if (possibleSuffix != null)
                            return possibleSuffix.Equals(icArray[8].ToString());
                        break;
                    case "P":
                        id = id.ToUpper();
                        return Regex.IsMatch(id, "^[A-Z0-9]*$");
                    case "O":
                        return true;
                }

                return false;
            }
            catch (Exception ex)
            {
                return false;
            }
        }

        public static JObject ExcludeJObjectVariables(JObject jo, JArray ja)
        {
            JObject processedJo = new JObject(jo);
            foreach (JToken jt in ja)
            {
                processedJo.Remove(jt.ToString());
            }
            return processedJo;
        }

        public static string ComputeSha256Hash(string rawData)
        {
            try
            {
                // Create a SHA256   
                using (SHA256 sha256Hash = SHA256.Create())
                {
                    // ComputeHash - returns byte array
                    byte[] bytes = sha256Hash.ComputeHash(Encoding.UTF8.GetBytes(rawData));

                    // Convert byte array to base64
                    return Convert.ToBase64String(bytes);
                }
            }
            catch (Exception ex)
            {
                LogData_Thread($"ComputeSha256Hash exception: {ex}", 2);
                return null;
            }
        }

        public static string ComputeHashToBase64WithKey(string rawData, string key)
        {
            try
            {
                string hashString = "";
                string final = rawData.Replace(System.Environment.NewLine, string.Empty);
                using (var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(key)))
                {
                    var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes($"{final}"));
                    hashString = BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();

                    // hashString contains the hashed string
                }
                return hashString;
            }
            catch (Exception ex)
            {
                LogData_Thread($"ComputeHash exception: {ex}", 2);
                return null;
            }
        }

        public static string EncodeBase64(string inputString)
        {
            //Added replace "/r/n" to string.Empty so that it work on linux environment as well
            var base64String = Convert.ToBase64String(Encoding.UTF8.GetBytes(inputString.Replace(System.Environment.NewLine, string.Empty)));
            return base64String;
        }

        public static string EncodeUrlString(string base64String)
        {
            base64String = base64String.Replace("+", "-").Replace("/", "_").TrimEnd('=');
            return base64String;
        }

        public static string DecodeUrlString(string base64UrlEncoded)
        {
            string base64Encoded = base64UrlEncoded.Replace('-', '+').Replace('_', '/');
            switch (base64Encoded.Length % 4)
            {
                case 2: base64Encoded += "=="; break;
                case 3: base64Encoded += "="; break;
            }
            return base64Encoded;
        }

        public static (bool, JObject) VerifyToppanJWT(string jwt, string ip, string secretKey)
        {
            string[] jwtSplit = jwt.Split(".");
            dynamic payload = new JObject();
            if (jwtSplit.Length != 3) return (false, payload);

            try
            {
                dynamic header = JObject.Parse(Encoding.UTF8.GetString(Convert.FromBase64String(DecodeUrlString(jwtSplit[0]))));
                payload = JObject.Parse(Encoding.UTF8.GetString(Convert.FromBase64String(DecodeUrlString(jwtSplit[1]))));
                string signature = Encoding.UTF8.GetString(Convert.FromBase64String(DecodeUrlString(jwtSplit[2])));

                var hashString = GenerateToppanJWTSignature($"{header}", $"{payload}", ip + secretKey);
                bool isValidSignature = signature.Equals(hashString);
                return (isValidSignature, payload);
            }
            catch (Exception ex)
            {
                return (false, payload);
            }
        }

        public static string EncodeToppanJWT(string ip, string secretKey, int licenseStatus, string[] serviceIds)
        {
            dynamic header = GenerateToppanJWTHeader("JWT", SecurityAlgorithms.HmacSha256);

            dynamic payload = GenerateToppanJWTPayload("TOPPAN", licenseStatus, DateTime.Now.ToEpochTime(), serviceIds);

            CommonHelper.DisplayConsole($"------- {ip + secretKey}");

            var hashString = GenerateToppanJWTSignature($"{header}", $"{payload}", ip + secretKey);
          
            return $"{EncodeUrlString(EncodeBase64(header.ToString()))}." +
                $"{EncodeUrlString(EncodeBase64(payload.ToString()))}." +
                $"{EncodeUrlString(EncodeBase64(hashString))}";
        }

        public static JObject GenerateToppanJWTHeader(string typ, string alg)
            => new JObject() { { "typ", typ }, { "alg", alg } };

        public static JObject GenerateToppanJWTPayload(string iss, int licenseStatus, long epochTime, string[] serviceIds)
        {
            if(serviceIds == null)
                serviceIds = new string[] {""};

            return new JObject() { { "iss", iss }, { "licenseStatus", licenseStatus }, { "responseDate", epochTime }, { "serviceIds", JArray.FromObject(serviceIds) } };
        }
            

        public static string GenerateToppanJWTSignature(string header, string payload, string key)
            => ComputeHashToBase64WithKey($"{header}.{payload}", key);

        public static string GetLocalIP()
        {
            try
            {
                var host = System.Net.Dns.GetHostEntry(System.Net.Dns.GetHostName());
                foreach (var ip in host.AddressList)
                {
                    if (ip.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)
                    {
                        return ip.ToString();
                    }
                }
            }
            catch (Exception ex)
            {

            }
            return "127.0.0.1";
        }

        public static void CheckAndKillExistingInstances()
        {
            try
            {
                bool isFirstInstance = false;
                Process currentProcess = Process.GetCurrentProcess();
                Process[] processes = Process.GetProcessesByName(currentProcess.ProcessName);
                if (processes.Length > 1)
                {
                    foreach (Process process in processes)
                    {
                        if (process.Id != currentProcess.Id && process.MainModule.FileName == currentProcess.MainModule.FileName)
                        {
                            isFirstInstance = false;
                            break;
                        }
                    }

                    if (isFirstInstance == false)
                    {
                        // Kill the existing instance
                        foreach (Process process in processes)
                        {
                            if (process.Id != currentProcess.Id && process.MainModule.FileName == currentProcess.MainModule.FileName)
                            {
                                process.Kill();
                            }
                        }
                    }
                }
            }
            catch(Exception ex)
            { }
        }


        #region zeromq Cryptographic
        public static string EncryptZeromqMessage(string Message, int addDays = 0)
        {
            string sretval = "";
            string header = "SENTIER";
            byte[] bsHeader = Encoding.UTF8.GetBytes(header);
            try
            {
                byte[] plaintextBytes = Encoding.UTF8.GetBytes(Message);
                dynamic aesKey = GetZeromqKey(addDays);
                byte[] encryptedBytes = AES256_Encrypt(aesKey, plaintextBytes);
                sretval = BitConverter.ToString(bsHeader).Replace("-", "");
                sretval += BitConverter.ToString(encryptedBytes).Replace("-", "");
            }
            catch (Exception ex)
            { }
            return sretval;
        }

        public static string DecryptZeromqMessage(string Message, int addDays = 0)
        {
            string sretval = Message;
            string header = "SENTIER";
            try
            {
                string sFmt = "HH:mm:ss.ffff";
                System.Diagnostics.Debug.WriteLine($"{System.DateTime.Now.ToString(sFmt)} Start decrypting message....");
                if (!string.IsNullOrEmpty(Message))
                {
                    byte[] messagebytes = StringToByteArray(Message);
                    var bHeader = new byte[header.Length];
                    Buffer.BlockCopy(messagebytes, 0, bHeader, 0, bHeader.Length);
                    var dHeader = Encoding.UTF8.GetString(bHeader);
                    if (header == dHeader)
                    {
                        dynamic aesKey = GetZeromqKey(addDays);
                        byte[] encryptedbytes = new byte[messagebytes.Length - dHeader.Length];
                        Buffer.BlockCopy(messagebytes, dHeader.Length, encryptedbytes, 0, encryptedbytes.Length);
                        var decryptedBytes = AES256_Decrypt(aesKey, encryptedbytes);
                        sretval = Encoding.UTF8.GetString(decryptedBytes);
                    }
                }
                System.Diagnostics.Debug.WriteLine($"{System.DateTime.Now.ToString(sFmt)} Done decrypting message....");
            }
            catch (Exception ex)
            { }
            return sretval;
        }

        public static byte[] StringToByteArray(string hex)
        {
            return Enumerable.Range(0, hex.Length)
                             .Where(x => x % 2 == 0)
                             .Select(x => Convert.ToByte(hex.Substring(x, 2), 16))
                             .ToArray();
        }


        public static dynamic GetZeromqKey(int additionalday = 0)
        {
            dynamic dyRetval = new JObject();
            try
            {
                string sFmt = "yyyyMMdd";
                DateTime dtKey = System.DateTime.Now.AddDays(additionalday);
                string publickey = dtKey.ToString(sFmt);
                string privatekey = $"Toppan-{dtKey.ToString(sFmt)}-tss";

                using (System.Security.Cryptography.SHA512 sha512 = System.Security.Cryptography.SHA512.Create())
                {
                    byte[] inputBytes = Encoding.UTF8.GetBytes(publickey);
                    byte[] hashBytes = sha512.ComputeHash(inputBytes);
                    dyRetval.iv = Shuffle_IV_Zeromq(hashBytes);
                    inputBytes = Encoding.UTF8.GetBytes(privatekey);
                    hashBytes = Shuffle_Key_Zeromq(sha512.ComputeHash(inputBytes));
                    dyRetval.key = hashBytes;

                }

            }
            catch (Exception ex)
            { }

            return dyRetval;
        }

        public static byte[] AES256_Encrypt(dynamic aesKey, byte[] content)
        {
            byte[] ciphertextBytes = null;
            try
            {
                using (var aes = new AesManaged())
                {
                    aes.Key = aesKey.key;
                    aes.IV = aesKey.iv;
                    aes.Mode = CipherMode.CBC;
                    using (var encryptor = aes.CreateEncryptor())
                    {
                        ciphertextBytes = encryptor.TransformFinalBlock(content, 0, content.Length);
                    }
                }
            }
            catch (Exception ex)
            { }
            return ciphertextBytes;
        }


        public static byte[] AES256_Decrypt(dynamic aesKey, byte[] encryptedContent)
        {
            byte[] decryptedPlaintext = null;
            try
            {
                using (var aes = new AesManaged())
                {
                    aes.Key = aesKey.key;
                    aes.IV = aesKey.iv;
                    aes.Mode = CipherMode.CBC;
                    using (var decryptor = aes.CreateDecryptor())
                    {
                        decryptedPlaintext = decryptor.TransformFinalBlock(encryptedContent, 0, encryptedContent.Length);
                    }
                }
            }
            catch
            { }
            return decryptedPlaintext;
        }


        private static byte[] Shuffle_IV_Zeromq(byte[] key)
        {
            byte[] byRetval = null;
            int[] pos = new int[] { 50, 20, 7, 42 };
            int len = 4;
            int keylen = 16;
            try
            {
                int dPos = 0;
                byRetval = new byte[keylen];
                foreach (var p in pos)
                {
                    Array.Copy(key, p, byRetval, dPos, len);
                    dPos += len;
                }
            }
            catch (Exception ex)
            { }

            return byRetval;
        }

        private static byte[] Shuffle_Key_Zeromq(byte[] key)
        {
            byte[] byRetval = null;
            int[] pos = new int[] { 35, 27, 42, 2, 15, 7, 6, 52 };
            int len = 4;
            int keylen = 32;
            try
            {
                int dPos = 0;
                byRetval = new byte[keylen];
                foreach (var p in pos)
                {
                    Array.Copy(key, p, byRetval, dPos, len);
                    dPos += len;
                }

            }
            catch (Exception ex)
            { }

            return byRetval;
        }
        #endregion zerome Cryptographic


        #region Extensions
        public static IEnumerable<(T item, int index)> WithIndex<T>(this IEnumerable<T> source)
            => source.Select((item, index) => (item, index));

        public static bool EqualsIgnore(this string source, string input)
            => source.Equals(input, StringComparison.OrdinalIgnoreCase);

        public static bool ContainsIgnore(this string[] source, string input)
            => source.Contains(input, StringComparer.InvariantCultureIgnoreCase);

        public static bool JSON_TryParse(this string content, out JObject ReturnObject)
        {
            bool bretval = false;
            ReturnObject = null;
            try
            {
                ReturnObject = JObject.Parse(content);
                if (ReturnObject != null)
                    bretval = true;
            }
            catch
            {
                return false;
            }
            return bretval;
        }

        public static DateTime GetDate(this string input)
        {
            try
            {
                var formatStrings = new string[] { "yyyy-MM-dd", "dd-MM-yyyy", "MM-dd-yyyy", "yyyy/MM/dd", "dd/MM/yyyy", "MM/dd/yyyy", "MM/dd/yyyy hh:mm:ss tt", "yyyy-MM-dd hh:mm:ss" };
                if (DateTime.TryParseExact(input, formatStrings, CultureInfo.CurrentCulture, DateTimeStyles.None, out DateTime dateValue))
                    return dateValue;
            }
            catch (Exception ex)
            {
                DisplayConsole($"GetDate exception: {ex}");
            }
            return DateTime.MinValue;
        }

        public static bool IsBase64String(this string s)
        {
            try
            {
                if (string.IsNullOrEmpty(s)) return false;
                byte[] data = Convert.FromBase64String(DecodeUrlString(s));
                return true;
            }
            catch (FormatException)
            {
                return false;
            }
        }

        public static string ConvertBitmapToBase64String(this System.Drawing.Bitmap bm, System.Drawing.Imaging.ImageFormat format)
        {
            string sRetval = "";
            try
            {
                MemoryStream ms = new MemoryStream();
                bm.Save(ms, format);
                byte[] byteImage = ms.ToArray();
                sRetval = Convert.ToBase64String(byteImage);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }

            return sRetval;
        }

        public static string GetBase64Sting(this System.Drawing.Bitmap bmpImage, System.Drawing.Imaging.ImageFormat format = null)
        {
            string sRetval = "";
            try
            {
                if (bmpImage != null)
                {
                    //System.Drawing.ImageConverter converter = new System.Drawing.ImageConverter();
                    //byte[] bytes = (byte[])converter.ConvertTo(bmpImage, typeof(byte[]));
                    byte[] bytes = bmpImage.ImageToByte(format);
                    sRetval = Convert.ToBase64String(bytes); //Get Base64
                }
            }
            catch (Exception ex)
            {
                CommonHelper.DisplayConsole(ex.Message);
            }
            return sRetval;
        }

        public static byte[] ImageToByte(this System.Drawing.Bitmap bmpImage, System.Drawing.Imaging.ImageFormat format = null)
        {
            using (var stream = new MemoryStream())
            {
                if (format == null)
                    format = System.Drawing.Imaging.ImageFormat.Png;
                bmpImage.Save(stream, format);
                return stream.ToArray();
            }
        }

        public static ObservableCollection<T> ToObservableCollection<T>(this IEnumerable<T> col)
        {
            return new ObservableCollection<T>(col);
        }

        public static T GetEnum<T>(this string input)
        {
            try
            {
                return (T)Enum.Parse(typeof(T), input, true);
            }
            catch
            {
                return default(T);
            }
        }

        public static T GetEnum<T>(this int input)
        {
            return input.ToString().GetEnum<T>();
        }

        public static DateTime EpochTimeToDateTime(this long epochTime)
        {
            return new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc).AddSeconds(epochTime).ToLocalTime();
        }

        public static long ToEpochTime(this DateTime date)
        {
            DateTime origin = new DateTime(1970, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc);
            TimeSpan diff = date.ToUniversalTime() - origin;
            return (long)Math.Floor(diff.TotalSeconds);
        }

        public static bool IsNullOrEmpty(this JToken token)
        {
            return (token == null) ||
                   (token.Type == JTokenType.Array && !token.HasValues) ||
                   (token.Type == JTokenType.Object && !token.HasValues) ||
                   (token.Type == JTokenType.String && token.ToString() == String.Empty) ||
                   (token.Type == JTokenType.Null);
        }

        
        #endregion Extensions

        #region private methods
        private static void LogMessage(string Message, int LogType = 1, bool logConsole = false)
        {
            try
            {
                switch (LogType)
                {
                    case 0:
                        // Dont write in log file
                        break;
                    case 1:
                        logger?.Information(Message);
                        break;
                    case 2:
                        logger?.Error(Message);
                        break;
                    case 4:
                        logger?.Verbose(Message);
                        break;
                    case 8:
                        logger?.Debug(Message);
                        break;
                }

                if (logConsole) DisplayConsole(Message);
            }
            catch (Exception ex)
            {
                DisplayConsole(ex.ToString());

            }
        }
        #endregion private methods
    }
}
