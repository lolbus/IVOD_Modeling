using CommonUtilities.Helpers;
using SuperSocket.ClientEngine;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using WebSocket4Net;

namespace CommonUtilities.Connection
{
    public class WebSocketClient : IDisposable
    {
        private SynchronizationContext _context;

        public WebSocket webSocketClient;
        public event EventHandler Connecting;
        public event EventHandler Connected;
        public event EventHandler Disconnected;
        public event EventHandler<ErrorEventArgs> Error;
        public event EventHandler<MessageReceivedEventArgs> MessageReceived;

        public string url = "";

        public WebSocketClient(string url)
        {
            try
            {
                this.url = url;
                webSocketClient = new WebSocket(url);
                _context = SynchronizationContext.Current;

                webSocketClient.MessageReceived += WebSocketClient_MessageReceived;
                webSocketClient.Error += WebSocketClient_Error;

                webSocketClient.Opened += delegate
                {
                    RaiseEvent(Connected);
                };
                webSocketClient.Closed += delegate
                {
                    RaiseEvent(Disconnected);

                    Task.Delay(10000).Wait();
                    Connect();
                };
            }
            catch (Exception)
            {
                throw;
            }
        }

        public void Connect()
        {
            try
            {
                RaiseEvent(Connecting);

                Task.Delay(1000).Wait();
                webSocketClient.Open();
            }
            catch (Exception)
            {
                throw;
            }
        }

        public void Disconnect()
        {
            try
            {
                webSocketClient.Close();
            }
            catch (Exception)
            {
                throw;
            }
        }

        public void SendMessage(string message)
        {
            try
            {
                webSocketClient.Send(message);
            }
            catch (Exception)
            {
                throw;
            }
        }

        private void WebSocketClient_Opened(object sender, EventArgs e)
        {
            try
            {
                CommonHelper.LogData_Thread("WebSocketClient_Opened", 0, true);
            }
            catch (Exception)
            {
                throw;
            }
        }

        private void WebSocketClient_Closed(object sender, EventArgs e)
        {
            try
            {
                CommonHelper.LogData_Thread("WebSocketClient_Closed", 0, true);
            }
            catch (Exception)
            {
                throw;
            }
        }

        private void WebSocketClient_Error(object sender, ErrorEventArgs e)
        {
            try
            {
                CommonHelper.LogData_Thread($"WebSocketClient_Error: {e.Exception}", 0, true);
                RaiseEvent(Error, new ErrorEventArgs(e.Exception));
            }
            catch (Exception)
            {
                throw;
            }
        }

        private void WebSocketClient_MessageReceived(object sender, MessageReceivedEventArgs e)
        {
            try
            {
                RaiseEvent(MessageReceived, new MessageReceivedEventArgs(e.Message));
            }
            catch (Exception)
            {
                throw;
            }
        }

        protected void RaiseEvent<T>(EventHandler<T> handler, T args) //where T : EventArgs
        {
            try
            {
                if (handler != null)
                {
                    if (_context != null)
                    {
                        _context.Post(new SendOrPostCallback(_ => handler(this, args)), null);
                    }
                    else
                    {
                        handler(this, args);
                    }
                }
            }
            catch (Exception)
            {
                throw;
            }
        }

        protected void RaiseEvent(EventHandler handler)
        {
            try
            {
                if (handler != null)
                {
                    if (_context != null)
                    {
                        _context.Post(new SendOrPostCallback(_ => handler(this, EventArgs.Empty)), null);
                    }
                    else
                    {
                        handler(this, EventArgs.Empty);
                    }
                }
            }
            catch (Exception)
            {
                throw;
            }
        }

        public void Dispose()
        {
            try
            {
                webSocketClient.Dispose();
            }
            catch (Exception)
            {
                throw;
            }
        }
    }
}
