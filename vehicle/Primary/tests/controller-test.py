# Prints names of all inputs recieved, with respective states.
from inputs import get_gamepad

while True:
  events = get_gamepad()
  for event in events:
    print(event.code, event.state)
