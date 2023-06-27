using CommonUtilities.Helpers;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace CommonUtilities.Connection.SignalR
{
    public class GateClient : ApiBase, IDisposable
    {
        string _url;
        private string _clientId;
        private Dictionary<string, string> _queryString;
        HubClient _hubClient;
        private SynchronizationContext _context;
        private dynamic settings = new JObject();

        private const string HUB_NAME = "AdminHub";
        const string SendMessageUrl = "message/SendMessage";
        const string UpdateGateUrl = "gate/UpdateGate";
        const string UpdateGateDoorUrl = "gate/UpdateGateDoor";
        const string GetGateUrl = "gate/getGateByCode";
        const string GetLocationsUrl = "location/getlocations";

        public event EventHandler Disconnected;
        public event EventHandler Connecting;
        public event EventHandler Connected;
        public event EventHandler ConnectionError;
        public event EventHandler<GateDoorEventArgs> GateDoorUpdated;

        public GateClient(dynamic settings) : this($"{settings.username}", $"{settings.psw}", $"{settings.url}", $"{settings.clientId}", false)
        {
            this.settings = settings;
        }

        public GateClient(string username, string psw, string url, string clientId, bool sendKeepAlive) : base(username, psw, url)
        {
            _url = url;
            _clientId = clientId;
            _queryString = new Dictionary<string, string>();
            _queryString.Add("clientId", _clientId);
            _context = SynchronizationContext.Current;
        }


        public async Task Connect()
        {
            try
            {
                if (_hubClient == null)
                {
                    _hubClient = new HubClient(_url, HUB_NAME, _queryString);
                    SubscribeHubConnection();
                    SubscribeiGateHub();
                }
                await _hubClient.Connect();
            }
            catch (Exception ex)
            {
                CommonHelper.LogData_Thread($"{ex}", 0, true);
            }
        }

        private void SubscribeHubConnection()
        {
            _hubClient.Disconnected += delegate { RaiseEvent(Disconnected); };
            _hubClient.Reconnecting += delegate { RaiseEvent(Connecting); };
            _hubClient.Reconnected += delegate { RaiseEvent(Connected); };
            _hubClient.ConnectionError += delegate { RaiseEvent(ConnectionError); };
        }

        private void SubscribeiGateHub()
        {
            _hubClient.Subscribe<JObject>($"{settings.eventName}", req => RaiseEvent(GateDoorUpdated, new GateDoorEventArgs(req)));
        }

        public async Task SendMessage(string url, dynamic metadata)
        {
            await PostAsJsonAsync(url, metadata);
        }

        public class GateDoorEventArgs : EventArgs
        {
            public dynamic RequestInfo { get; }

            public GateDoorEventArgs(dynamic value)
            {
                RequestInfo = value;
            }
        }

        protected void RaiseEvent<T>(EventHandler<T> handler, T args)
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

        protected void RaiseEvent(EventHandler handler)
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
            _hubClient?.Dispose();
            Client?.Dispose();
        }
    }
}
