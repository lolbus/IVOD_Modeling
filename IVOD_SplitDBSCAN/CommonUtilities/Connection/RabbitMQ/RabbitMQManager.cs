using CommonUtilities.Helpers;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CommonUtilities.Connection.RabbitMQ
{
    public class RabbitMQManager : IDisposable
    {
        private readonly IConnection listenConnection;
        private readonly IModel channel;
        private IModel sendChannel;

        public RabbitMQManager(string hostName, string userName, string password, int port)
        {
            var connectionFactory = new ConnectionFactory()
            {
                HostName = hostName,
                UserName = userName,
                Password = password,
                Port = port,
            };
            connectionFactory.RequestedHeartbeat = new TimeSpan(0, 0, 60);
            listenConnection = connectionFactory.CreateConnection();
            channel = listenConnection.CreateModel();
        }

        public string CreateQueue(string exchange, string routingKey)
        {
            var queueResult = channel.QueueDeclare();
            var queueId = queueResult.QueueName;
            channel.QueueBind(queueId, exchange, routingKey);
            return queueId;
        }


        public void SendMessage(string exchange, string routingKey, string message, bool persistent = false)
        {
            if (channel != null)
            {


                var body = Encoding.UTF8.GetBytes(message);
                var properties = channel.CreateBasicProperties();
                if (persistent)
                {
                    properties.Persistent = true;
                }
                channel.BasicPublish(exchange, routingKey, properties, body);
            }
        }

        public void SendMessage(string hostName, string userName, string password, int port, string exchange, string routingKey, string message, bool persistent = false)
        {
            if (sendChannel == null)
            {
                var connectionFactory = new ConnectionFactory()
                {
                    HostName = hostName,
                    UserName = userName,
                    Password = password,
                    Port = port,
                };
                connectionFactory.RequestedHeartbeat = new TimeSpan(0, 0, 60);
                var sendConnection = connectionFactory.CreateConnection();
                sendChannel = sendConnection.CreateModel();
            }
            var body = Encoding.UTF8.GetBytes(message);
            var properties = sendChannel.CreateBasicProperties();
            if (persistent)
            {
                properties.Persistent = true;
            }
            sendChannel.BasicPublish(exchange, routingKey, properties, body);
        }

        public void ReceiveMessages(string queueId, Action<string> messageReceivedCallback)
        {
            var consumer = new EventingBasicConsumer(channel);
            consumer.Received += (model, ea) =>
            {
                var body = ea.Body.ToArray();
                var message = Encoding.UTF8.GetString(body);
                messageReceivedCallback(message);
            };
            channel.BasicConsume(queueId, true, consumer);
        }

        public void Dispose()
        {
            channel?.Close();
            listenConnection?.Close();
        }
    }
}
