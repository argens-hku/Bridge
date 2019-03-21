def main ():
	network_1 = ""
	network_2 = ""
	network_3 = ""
	network_4 = ""

	agent_1 = Agent (network_1)
	agent_2 = Agent (network_1)
	agent_3 = Agent (network_1)
	agent_4 = Agent (network_1)

	agents = [agent_1, agent_2, agent_3, agent_4]
	episodes = 1000
	for i in range (0, episodes):
		game = genGame ()
		result = play (networks, game)
		for i in range (0, 4):
			agent [i].learn (result)
		if i % 100 == 0:
			for i in range (0, 4):
				agent.saveNetwork (i)