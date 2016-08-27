import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint

        # TODO: Initialize any additional variables here
        self.next_waypoint = None
        self.state = []
        self.q_table = {}
        self.alpha = 0.5 # Learning rate
        self.gamma = 0.5 # Discount factor
        self.actions = Environment.valid_actions

    def reset(self, destination=None):
        self.planner.route_to(destination)
        
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.next_waypoint = None
        self.state = []

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        state = (self.next_waypoint, inputs['light'], inputs['oncoming'], inputs['left'])
        self.state = state
        
        # TODO: Select action according to your policy
        action = self.choose_action(state)

        # Execute action and get reward
        reward = self.env.act(self, action)
        
        # Learn policy based on state, action, reward
        self.learn_q(state, action, reward)

        print "LearningAgent.update(): state = {}, action = {}, reward = {}, deadline = {}".format(state, action, reward, deadline)  # [debug]

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        q_value = [self.get_q(state, action) for action in self.actions]
        
        maxQ = max(q_value)
        
        count = q_value.count(maxQ)
        if count > 1:
            best = [i for i in range(len(self.actions)) if q_value[i] == maxQ]
            i = random.choice(best)
        else:
            i = q_value.index(maxQ)
        action = self.actions[i]
        return action

    def learn_q(self, state, action, reward):
        new_state = state
        maxqnew = self.get_q(new_state, action)
        self.q_table[(state, action)] = ((1 - self.alpha) * self.get_q(state, action)) + self.alpha * (reward + self.gamma * maxqnew)

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.000000005, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
