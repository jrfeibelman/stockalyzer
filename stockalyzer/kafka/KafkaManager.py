from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
from stockalyzer.core.Logger import Logger
from json import dumps, loads
from threading import Timer as Thread_Timer

class KafkaManager:

    __slots__ = '_hosts', '_consumer', '_producer', '_callbacks', '_timer', '_sleepTime', '_initialized'
    
    def __init__(self, sleepTime=1):
        # FIXME extend this to aggregate data from multiple kafka instances
        self._callbacks = dict()
        self._sleepTime = sleepTime
        self._hosts = []
        self._initialized = False

    def initialize(self, config):
        self.init_connections(config.expand('KafkaConnection'))

        # TODO - asynchronously await for connectivity to be established 

        if not self.init_pubs(config.expand('KafkaSession')):
            Logger().error("Failed to initialize Kafka publishers. Exiting")
            return False
        if not self.init_subs(config.expand('KafkaSession')):
            Logger().error("Failed to initialize Kafka subscribers. Exiting")
            return False

        self._initialized = True
        return True

    def init_connections(self, cfg):
        for key in cfg.getDict():
            host = cfg.expand(key).get_value('Primary', 'INVALID')
            
            if host == "INVALID":
                Logger().error("Received invalid host %s for amps connection %s. Exiting" % (host, key))
                return False

            self._hosts.append(host)

        return True

    def init_pubs(self, cfg):
        for key in cfg.getDict():
            pubTopicCfg = cfg.expand(key).expand('PublishTopics')

            if pubTopicCfg.isEmpty():
                Logger().warn("No kafka publishers configured")
                return True

            for topicKey in pubTopicCfg.getDict():
                Logger().debug("Topic: %s" % topicKey)
                topic = pubTopicCfg.expand(topicKey).get_value("Topic", 'INVALID')

            if topic == "INVALID":
                Logger().error("Failed to initialize kafka publisher [%s]" % (topic))
                return False

        try:
            self._producer = KafkaProducer(
                bootstrap_servers=self._hosts,
                value_serializer=lambda v: dumps(v).encode('utf-8')
            )
        except NoBrokersAvailable:
            Logger().error("Could not establish a connection to Kafka Servers %s" % self._hosts)
            return False


        return True

    def init_subs(self, cfg):
        for key in cfg.getDict():
            subTopicCfg = cfg.expand(key).expand('SubscribeTopics')

            if subTopicCfg.isEmpty():
                Logger().warn("No kafka subscribers configured")
                return True

            for topicKey in subTopicCfg.getDict():
                topic = subTopicCfg.expand(topicKey).get_value("Topic", 'INVALID')
                command = subTopicCfg.expand(topicKey).get_value("Command", 'INVALID')

                if topic == "INVALID" or command == "INVALID" or not self.register_topic(topic):
                    Logger().error("Failed to initialize kafka subscription [%s]:[%s]" % (topic, command))
                    return False

        try:
            self._consumer = KafkaConsumer(
                client_id='stockalyzer-01',
                bootstrap_servers=self._hosts,
                auto_offset_reset='earliest' if "query" in command else 'latest',
            )
        except NoBrokersAvailable:
            Logger().error("Could not establish a connection to Kafka Servers %s" % self._hosts)
            return False


        return True

    def testCallback(self, data):
        Logger().debug('Callback triggered for data %s' % data)

    def register_topic(self, topic_name):
        if topic_name == "ReferenceDataTopic":
            callback = None
        elif topic_name == "StrategyIndicatorTopic":
            callback = None
        elif topic_name == "StatsTopic":
            callback = None
        elif topic_name == "test":
            callback = print
        elif topic_name == "test2":
            callback = print
        else:
            Logger().error("Tried to register invalid topic %s" % topic_name)
            return False

        self._callbacks[topic_name] = callback
        return True

    def subscribe(self):
        if not self._initialized:
            Logger().warn("Kafka Subscriptions failed - could not connect to kafka server")
            return

        self._consumer.subscribe(topics=self._callbacks.keys())
        self._timer = Thread_Timer(self._sleepTime, self.poll)
        self._timer.start()

    def publish(self, topic, json_dict):
        self._producer.send(topic, json_dict)

    def poll(self):
        # print('polling...')
        records = self._consumer.poll(timeout_ms=1000)
        for t, consumer_records in records.items():
            topic = t.topic
            for consumer_record in consumer_records:
                Logger().debug("Received Kafka msg from topic %s : %s" % (topic, consumer_record.value.decode('utf-8')))
                self._callbacks[topic](consumer_record)
            continue

        self._timer = Thread_Timer(self._sleepTime, self.poll)
        self._timer.start()
