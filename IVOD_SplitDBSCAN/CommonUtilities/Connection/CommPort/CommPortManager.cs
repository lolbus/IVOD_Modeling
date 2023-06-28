using CommonUtilities.Helpers;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.IO.Ports;
using System.Linq;
using System.Management;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace CommonUtilities.Connection.CommPort
{
    public delegate void ComPortDataReceivedHandler(string result);
    public delegate void ComPortEventHandler();
    public delegate void ComPortErrorHandler(Exception ex);

    public class CommPortManager
    {
        public event ComPortDataReceivedHandler OnDataReceived;
        public event ComPortEventHandler OnOpen;
        public event ComPortEventHandler OnClose;
        public event ComPortErrorHandler OnErrorHandler;

        private SerialPort serialPort;

        private string comPort;
        public string ComPort
        {
            get { return comPort; }
            set { comPort = value; }
        }

        private int baudRate;
        public int BaudRate
        {
            get { return baudRate; }
            set { baudRate = value; }
        }

        private int parity;
        public int _Parity
        {
            get { return parity; }
            set { parity = value; }
        }

        private int dataBits;
        public int _DataBits
        {
            get { return dataBits; }
            set { dataBits = value; }
        }

        private int stopBits;
        public int _StopBits
        {
            get { return stopBits; }
            set { stopBits = value; }
        }

        private string deviceID;
        public string _DeviceID
        {
            get { return deviceID; }
            set { deviceID = value; }
        }


        public CommPortManager(string deviceID)
        {
            this.deviceID = deviceID;
            WqlEventQuery _q = new WqlEventQuery("__InstanceOperationEvent", "TargetInstance ISA 'Win32_USBControllerDevice' ");
            _q.WithinInterval = TimeSpan.FromSeconds(1);
            ManagementEventWatcher _w = new ManagementEventWatcher(_q);
            _w.EventArrived += onEventArrived;
            _w.Start();
        }

        private void onEventArrived(object sender, EventArrivedEventArgs e)
        {
            if (e.NewEvent["TargetInstance"] is ManagementBaseObject _o)
            {
                using (ManagementObject mo = new ManagementObject(_o["Dependent"].ToString()))
                {
                    if (mo != null)
                    {
                        try
                        {
                            string s = mo.GetPropertyValue("DeviceID").ToString();
                            s = mo.Properties["DeviceID"].Value.ToString();

                            if (s == deviceID)
                            {
                                //connected
                                CommonHelper.LogData_Thread($"{deviceID} connected.", 0, true);
                            }
                        }
                        catch (ManagementException ex)
                        {
                            string strDevice = mo.Path.RelativePath;
                            string[] strDeviceID = new string[] {};
                            //somewhere in your code
                            strDeviceID = strDevice.Split('=');

                            var clean = Regex.Unescape(strDeviceID[1]);
                            clean = clean.Replace("\"", "");

                            if (deviceID.EqualsIgnore(clean))
                            {
                                //disconnected
                                CommonHelper.LogData_Thread($"{deviceID} disconnected.", 0, true);
                                TriggerEvent(OnClose);
                            }
                        }
                    }
                }
            }
        }

        public Parity SetParity(int parity)
        {
            Parity result = new Parity();
            switch (parity)
            {
                case 1:
                    {
                        result = Parity.Odd;
                        break;
                    }
                case 2:
                    {
                        result = Parity.Even;
                        break;
                    }
                case 3:
                    {
                        result = Parity.Mark;
                        break;
                    }
                case 4:
                    {
                        result = Parity.Space;
                        break;
                    }
                default:
                    {
                        result = Parity.None;
                        break;
                    }
            }
            return result;
        }

        public StopBits SetStopBits(int stopBits)
        {
            StopBits result = new StopBits();
            switch (stopBits)
            {
                case 1:
                    {
                        result = StopBits.One;
                        break;
                    }
                case 2:
                    {
                        result = StopBits.Two;
                        break;
                    }
                case 3:
                    {
                        result = StopBits.OnePointFive;
                        break;
                    }
                default:
                    {
                        result = StopBits.None;
                        break;
                    }
            }
            return result;
        }


        private byte[] HexToByte(string msg)
        {
            //remove any spaces from the string
            msg = msg.Replace(" ", "");
            //create a byte array the length of the
            //divided by 2 (Hex is 2 characters in length)
            byte[] comBuffer = new byte[msg.Length / 2];
            //loop through the length of the provided string
            for (int i = 0; i < msg.Length; i += 2)
                //convert each set of 2 characters to a byte
                //and add to the array
                comBuffer[i / 2] = (byte)Convert.ToByte(msg.Substring(i, 2), 16);
            //return the array
            return comBuffer;
        }



        /// <summary>
        /// method to convert a byte array into a hex string
        /// </summary>
        /// <param name="comByte">byte array to convert</param>
        /// <returns>a hex string</returns>
        private string ByteToHex(byte[] comByte)
        {
            //create a new StringBuilder object
            StringBuilder builder = new StringBuilder(comByte.Length * 3);
            //loop through each byte in the array
            foreach (byte data in comByte)
                //convert the byte to a string and add to the stringbuilder
                builder.Append(Convert.ToString(data, 16).PadLeft(2, '0').PadRight(3, ' '));
            //return the converted value
            return builder.ToString().ToUpper();
        }


        public void OpenPort()
        {
            bool result = false;
            try
            {
                if (serialPort != null && serialPort.IsOpen)
                    serialPort.Close();

                serialPort = new SerialPort(ComPort, BaudRate, SetParity(_Parity), _DataBits, SetStopBits(_StopBits));
                serialPort.DataReceived += new SerialDataReceivedEventHandler(SerialPort_DataReceived);

                serialPort.Open();
                result = true;

                if (result)
                {
                    TriggerEvent(OnOpen);
                }
                else
                {
                    TriggerEvent(OnClose);
                }
            }
            catch (Exception ex)
            {
                TriggerEvent(OnClose);
                TriggerErrorEvent(ex);
            }

        }

        public bool ClosePort()
        {
            bool result = false;
            try
            {
                if (serialPort != null && serialPort.IsOpen)
                {
                    serialPort.DataReceived -= new SerialDataReceivedEventHandler(SerialPort_DataReceived);

                    serialPort.Close();
                    serialPort.Dispose();

                    result = true;
                }
            }
            catch (Exception ex)
            {
                TriggerErrorEvent(ex);
            }

            return result;
        }

        public void WriteData(string msg)
        {
            try
            {
                if (serialPort != null && serialPort.IsOpen)
                {
                    byte[] newMsg = HexToByte(msg);
                    serialPort.Write(newMsg, 0, newMsg.Length);
                }
            }
            catch (Exception ex)
            {
                TriggerErrorEvent(ex);
            }
        }

        private void SerialPort_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            try
            {
                int dataLength = serialPort.BytesToRead;
                byte[] comBuffer = new byte[dataLength];
                serialPort.Read(comBuffer, 0, dataLength);

                string data = Encoding.ASCII.GetString(comBuffer);
                string message = Regex.Replace(data, @"[^\t\r\n -~]", "");

                //finishedScanning = true;
                TriggerEvent_DateReceived(message);
            }
            catch (Exception ex)
            {
                TriggerErrorEvent(ex);
            }
        }

        private void TriggerEvent_DateReceived(string result)
        {
            try
            {
                if (OnDataReceived != null)
                {
                    System.Threading.Thread thread = new System.Threading.Thread(
                       new System.Threading.ThreadStart(
                           delegate ()
                           {
                               OnDataReceived.Invoke(result);
                           }));
                    thread.Start();
                }
            }
            catch (Exception ex)
            {
                TriggerErrorEvent(ex);
            }
        }

        private void TriggerEvent(ComPortEventHandler scnEvt)
        {
            if (scnEvt != null)
            {
                System.Threading.Thread thread = new System.Threading.Thread(
                   new System.Threading.ThreadStart(
                       delegate ()
                       {
                           scnEvt.Invoke();
                       }));
                thread.Start();
            }
        }

        private void TriggerErrorEvent(Exception ex)
        {
            if (OnErrorHandler != null)
            {
                System.Threading.Thread thread = new System.Threading.Thread(
                   new System.Threading.ThreadStart(
                       delegate ()
                       {
                           OnErrorHandler.Invoke(ex);
                       }));
                thread.Start();
            }
        }
    }
}
