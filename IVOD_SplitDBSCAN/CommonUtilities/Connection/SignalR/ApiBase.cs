using System;
using System.Net;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using HttpHeader = System.Collections.Generic.KeyValuePair<string, string>;
using System.Net.Http.Formatting;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace CommonUtilities.Connection.SignalR
{
    public class ApiBase
    {

        const string ContentTypeJson = "application/json";
        private Lazy<HttpClient> _client;
        public string HostUri { get; set; }
        protected string ApiPath { get; private set; }
        protected string AcceptType { get; private set; }
        private ICredentials _credentials { get; set; }
        protected HttpClient Client { get { return _client.Value; } }
        protected static readonly TimeSpan ApiTimeOut = TimeSpan.FromMinutes(5);

        public ApiBase(string username, string psw, string hostUri = null, string apiPath = "api/", string acceptType = "application/json")
        {
            HostUri = hostUri;
            ApiPath = apiPath;
            AcceptType = acceptType;

            _client = new Lazy<HttpClient>(() =>
            {
                var client = new HttpClient(new HttpClientHandler()
                {
                    Credentials = CreateCredentialCache(username, psw),
                    MaxRequestContentBufferSize = 1024 * 1024 * 10
                })
                {
                    BaseAddress = new Uri(new Uri(HostUri), ApiPath)
                };
                client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue(AcceptType));
                client.Timeout = ApiTimeOut;
                return client;
            });
        }


        private CredentialCache CreateCredentialCache(string username, string psw)
        {
            var credntialCache = new CredentialCache();
            credntialCache.Add(new Uri(HostUri), "Basic", new NetworkCredential() { UserName = username, Password = psw });
            return credntialCache;
        }

        protected void AddHeader(string key, string value)
        {
            if (Client.DefaultRequestHeaders.Contains(key))
                Client.DefaultRequestHeaders.Remove(key);
            Client.DefaultRequestHeaders.Add(key, value);
        }

        protected void ClearHeader(string key)
        {
            if (Client.DefaultRequestHeaders.Contains(key))
                Client.DefaultRequestHeaders.Remove(key);
        }

        public async Task<T> GetAsync<T>(string url, params HttpHeader[] headers)
        {
            var formatter = new JsonMediaTypeFormatter
            {
                SerializerSettings = { TypeNameHandling = TypeNameHandling.Auto }
            };
            var response = await Invoke(url, HttpMethod.Get, headers);
            var result = await response.Content.ReadAsAsync<T>(new MediaTypeFormatter[] { formatter });
            return result;
        }

        public async Task<string> GetStringAsync(string url, params HttpHeader[] headers)
        {
            var response = await Invoke(url, HttpMethod.Get, headers);
            var result = await response.Content.ReadAsStringAsync();
            return result;
        }

        public async Task<HttpResponseMessage> PostAsJsonAsync<TRequest>(string url, TRequest request, params HttpHeader[] headers)
        {
            return await Invoke(url, HttpMethod.Post, request, headers);
        }

        public async Task<HttpResponseMessage> PostAsync(string url)
        {
            return await Invoke(url, HttpMethod.Post, new HttpHeader[0]);
        }

        public async Task<HttpResponseMessage> PutAsJsonAsync<TRequest>(string url, TRequest request, params HttpHeader[] headers)
        {
            return await Invoke(url, HttpMethod.Put, request, headers);
        }

        public async Task<TResponse> PostAsJsonAsyncWithRequest<TRequest, TResponse>(string url, TRequest request, params HttpHeader[] headers)
        {
            var response = await Invoke(url, HttpMethod.Post, request, headers);
            return await response.Content.ReadAsAsync<TResponse>();
        }

        public async Task<HttpResponseMessage> PutAsync(string url, params HttpHeader[] headers)
        {
            return await Invoke(url, HttpMethod.Put, headers);
        }

        public async Task<HttpResponseMessage> DeleteAsync(string url, params HttpHeader[] headers)
        {
            return await Invoke(url, HttpMethod.Delete, headers);
        }

        public async Task<HttpResponseMessage> DeleteAsJsonAsync<T>(string url, T value, params HttpHeader[] headers)
        {
            return await Invoke(url, HttpMethod.Delete, value, headers);
        }

        public async Task<TT> DeleteAsJsonAsync<T, TT>(string url, T value, params HttpHeader[] headers)
        {
            var response = await Invoke(url, HttpMethod.Delete, value, headers);
            return await response.Content.ReadAsAsync<TT>();
        }

        public async Task<HttpResponseMessage> Invoke(string uri, HttpMethod method, params HttpHeader[] headers)
        {
            return await Invoke<Object>(uri, method, null, headers);
        }

#pragma warning disable RECS0017  //Disable warning possible compare of value type with null.
        public async Task<HttpResponseMessage> Invoke<T>(string uri, HttpMethod method, T value, params HttpHeader[] headers)
        {
            var request = new HttpRequestMessage(method, uri);
            if (value != null)
                request.Content = new ObjectContent<T>(value, new JsonMediaTypeFormatter(), (MediaTypeHeaderValue)null);
            foreach (var h in headers)
            {
                request.Headers.Add(h.Key, h.Value);
            }
            HttpResponseMessage response;
            try
            {
                response = await Client.SendAsync(request);
                if (response.IsSuccessStatusCode) return response;
            }
            catch (Exception ex)
            {
                throw ex.InnerException;
            }
            throw await ReconstituteException(response);
            //throw await ReconstituteException(response);
        }

        protected virtual async Task<ApiException> ReconstituteException(HttpResponseMessage response)
        {
            var contentType = response.Content.Headers.ContentType;
            if (contentType != null && contentType.MediaType == ContentTypeJson)
            {
                try
                {
                    var exObj = await response.Content.ReadAsAsync<JObject>();
                    var exceptionMessage = (string)exObj["ExceptionMessage"];
                    var message = (string)exObj["Message"];
                    var errorMessage = string.IsNullOrWhiteSpace(exceptionMessage) ? message : exceptionMessage;
                    if (errorMessage == null)
                        errorMessage = await response.Content.ReadAsStringAsync();
                    return new ApiException(response.StatusCode, errorMessage);
                }
                catch (Exception) { }
            }
            var unexpExc = await response.Content.ReadAsStringAsync();
            return new ApiException(response.StatusCode, $"An unexpected error occours.\n{unexpExc}");
        }
    }

    public class ApiException : Exception
    {
        public HttpStatusCode StatusCode { get; private set; }
        public ApiException(HttpStatusCode statusCode, string message) : base(message)
        {
            StatusCode = statusCode;
        }
        public ApiException(HttpStatusCode statusCode, string message, Exception innterException) : base(message, innterException)
        {
            StatusCode = statusCode;
        }

        public override string ToString()
        {
            return string.Format("Status={0}, Message={1}", StatusCode, base.Message + ", " + Message);
        }
    }
}
