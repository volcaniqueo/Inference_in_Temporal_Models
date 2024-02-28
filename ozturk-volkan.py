import sys

# Used to round the values to two decimal places, as requested in the project description.
def round_two_decimals(list):
    if isinstance(list, float):
        return round(list, 2)
    for i in range(len(list)):
        list[i] = round(list[i], 2)
    return list

# Hidden Markov Model class
# transition: transition probabilities
# emission: emission probabilities
# initial: initial (prior / belief) probabilities
# Provides sensor, normalize, forward and backward funcitons.
# Forward and backward functions does not return the normalized values.
class HiddenMarkovModel():
    def __init__(self, transition, emission, initial):
        self.transition = transition
        self.emission = emission
        self.initial = initial

    def sensor(self, e):
        if e == "T":
            return self.emission[0]
        else:
            return self.emission[1]
        
    def normalize(self, f):
        sum = f[0] + f[1]
        return [f[0] / sum, f[1] / sum]

    def forward(self, f, e):
        prediction = [0, 0]
        for i in range(2):
            prediction[0] += f[i] * self.transition[0][i]
            prediction[1] += f[i] * self.transition[1][i]
        sensor = self.sensor(e)
        message = [0, 0]
        for i in range(2):
            message[i] = prediction[i] * sensor[i]
        return message
    
    def backward(self, b, e):
        sensor = self.sensor(e)
        prediction = [0, 0]
        for i in range(2):
            prediction[i] = b[i] * sensor[i]
        message = [0, 0]
        for i in range(2):
            message[0] += prediction[i] * self.transition[0][i]
            message[1] += prediction[i] * self.transition[1][i]
        return message

# Recursive filtering function
def filtering(hmm, ev, i=0, f=None):
    if f is None:
        f = hmm.initial

    if i == len(ev):
        return f

    f = hmm.normalize(hmm.forward(f, ev[i]))
    return filtering(hmm, ev, i+1, f)

# Recursive likelihood function
def likelihood(hmm, ev, i=0, f=None):
    if f is None:
        f = hmm.initial

    if i == len(ev):
        return sum(f)

    f = hmm.forward(f, ev[i])
    return likelihood(hmm, ev, i+1, f)

# Smoothing function implemented using forward and backward algorithm
# k is the time point between 1 and t
def smoothing(hmm, ev, k):
    t = len(ev)

    fv = [[0.0, 0.0] for _ in range(t + 1)]
    b = [1.0, 1.0]
    sv = [[0.0, 0.0] for _ in range(t + 1)]

    fv[0] = hmm.initial

    for i in range(1, t + 1):
        fv[i] = hmm.forward(fv[i - 1], ev[i - 1])
    for i in range(t, -1, -1):
        temp = [0, 0]
        for j in range(2):
            temp[j] = fv[i][j] * b[j]
        sv[i - 1] = hmm.normalize(temp)
        b = hmm.backward(b, ev[i - 1])
    
    return sv[k]

# Viterbi algorithm for most likely explanation
def viterbi(hmm, ev):
    t = len(ev)

    m = [[0.0, 0.0] for _ in range(t)]
    m[0] = hmm.normalize(hmm.forward(hmm.initial, ev[0]))
    backtrack = []

    for i in range(1, t):
        temp1 = [0, 0]
        for j in range(2):
            temp1[j] = m[i - 1][j] * hmm.transition[0][j]
        temp2 = [0, 0]
        for j in range(2):
            temp2[j] = m[i - 1][j] * hmm.transition[1][j]
        temp3 = [0, 0]
        sensor = hmm.sensor(ev[i])
        temp3[0] = max(temp1) * sensor[0]
        temp3[1] = max(temp2) * sensor[1]
        m[i] = temp3
        backtrack.append([int(temp1[0] < temp1[1]), int(temp2[0] < temp2[1])])

    ml_path = [True] * t

    i_max = int(m[-1][0] < m[-1][1])

    for i in range(t - 1, -1, -1):
        ml_path[i] = not(bool(i_max))
        if i > 0:
            i_max = backtrack[i - 1][i_max]
    
    return ml_path, [round_two_decimals(i) for i in m]

    
    
    
         
# Program excepts seven inputs in a single line as requested in the project description.
#print("Usage: python <surname>-<name>.py <prob0> <prob1> <prob2> <prob3> <prob4> <type> <query>")

# Read the inpot from the command line
input = input()
input_list = input.split()

query = [input_list[6][1]] # Query
i = 7
while True:
    if input_list[i][-1] == "]":
        query.append(input_list[i][0])
        break
    else:
        query.append(input_list[i])
        i += 1


prior = [float(input_list[0]), 1 - float(input_list[0])]  # Prior probability of rain
transition = [[float(input_list[1]), float(input_list[2])], [1 - float(input_list[1]), 1 - float(input_list[2])]]  # Transition probabilities index 0 -> rain to rain, no rain to rain
emission = [[float(input_list[3]), float(input_list[4])], [1 - float(input_list[3]), 1 - float(input_list[4])]]  # Emission probabilities index 0 -> rain to umbrella, no rain to umbrella
type = input_list[5]  # Type of the query

hmm = HiddenMarkovModel(transition, emission, prior)  # Initialize the HMM

if type == "F":
    #print("Filtering")
    result = round_two_decimals(filtering(hmm, query))
    print("<" + str(result[0]) + ", " + str(result[1]) + ">")

elif type == "L":
    #print("Likelihood")
    result = round_two_decimals(likelihood(hmm, query))
    print("<" + str(result) + ">")

elif type == "S":
    #print("Smoothing")
    k = int(input_list[-1])
    result = round_two_decimals(smoothing(hmm, query, k))
    print("<" + str(result[0]) + ", " + str(result[1]) + ">")

elif type == "M":
    #print("Most Likely Explanation")
    result1, result2 = viterbi(hmm, query)
    print("[", end="")
    for i in range(len(result1)):
        if result1[i] == True:
            if i == len(result1) - 1:
                print("T", end="")
            else:
                print("T", end=" ")
        else:
            if i == len(result1) - 1:
                print("F", end="")
            else:
                print("F", end=" ")
    print("] ", end="")
    print("[", end="")
    for i in range(len(result2)):
        if i == len(result2) - 1:
            print("<" + str(result2[i][0]) + ", " + str(result2[i][1]) + ">", end="")
        else:
            print("<" + str(result2[i][0]) + ", " + str(result2[i][1]) + ">", end=", ")
    print("]")
    
    

