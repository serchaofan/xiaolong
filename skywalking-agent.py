from skywalking import agent, config
config.init(collector='192.168.10.71:11800', service='service-1')
agent.start()
