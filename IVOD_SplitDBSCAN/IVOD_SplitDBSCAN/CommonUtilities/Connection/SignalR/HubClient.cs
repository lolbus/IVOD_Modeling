using CommonUtilities.Helpers;
using Microsoft.AspNet.SignalR.Client;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace CommonUtilities.Connection.SignalR
{
    public class HubClient : IDisposable
    {
        private string _url;
        private IHubProxy _hubProxy;
        private HubConnection _connection;
        private bool _connectingInProgress;
        private bool _disposedCalled;
        private SynchronizationContext _context;

        public event EventHandler Disconnected;
        public event EventHandler Reconnecting;
        public event EventHandler Reconnected;
        public event EventHandler ConnectionError;

        public HubClient(string url, string hubName, IDictionary<string, string> queryString = null)
        {
            _url = url;
            _context = SynchronizationContext.Current;
            if (queryString == null)
                _connection = new HubConnection(url);
            else
                _connection = new HubConnection(url, queryString);

            _connection.JsonSerializer.TypeNameHandling = TypeNameHandling.Auto;
            _connection.StateChanged += _connection_StateChanged;
            _connection.Closed += _connection_Closed;
            _hubProxy = _connection.CreateHubProxy(hubName);
        }

        private void _connection_StateChanged(StateChange obj)
        {
            switch (obj.NewState)
            {
                case ConnectionState.Connecting:
                    {
                        RaiseEvent(Reconnecting);
                        break;
                    }
                case ConnectionState.Connected:
                    {
                        RaiseEvent(Reconnected);
                        break;
                    }
                case ConnectionState.Reconnecting:
                    {
                        RaiseEvent(Reconnecting);
                        break;
                    }
                case ConnectionState.Disconnected:
                    {
                        RaiseEvent(Disconnected);
                        break;
                    }
                default:
                    //Trace.WriteLine("Unknow connection state changed.");
                    break;
            }
        }

        public async Task Connect()
        {
            await TryConnect();
        }

        private async Task TryConnect()
        {
            _connectingInProgress = true;
            await CommonHelper.Run(async () => await _connection.Start(), OnConnectError, TimeSpan.FromSeconds(10));
            _connectingInProgress = false;
        }

        private bool OnConnectError(Exception ex)
        {
            RaiseEvent(ConnectionError);
            return true;
        }

        public void Invoke(string funcitonName, params object[] obj)
        {
            _hubProxy.Invoke(funcitonName, obj);
        }

        public void Subscribe(string eventName, Action action)
        {
            _hubProxy.On(eventName, action);
        }

        public void Subscribe<T>(string eventName, Action<T> action)
        {
            _hubProxy.On<T>(eventName, action);
        }

        private void _connection_Closed()
        {
            if (!_connectingInProgress && !_disposedCalled)
            {
                var _ = TryConnect();
            }
        }

        private void RaiseEvent(EventHandler handler)
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

        public void Dispose()
        {
            if (!_disposedCalled)
                _disposedCalled = true;
            if (_connection != null)
            {
                _connection.Stop(TimeSpan.FromSeconds(5));
                _connection.Dispose();
            }
        }
    }
}
