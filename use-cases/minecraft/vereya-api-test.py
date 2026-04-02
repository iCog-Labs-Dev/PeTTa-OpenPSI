import time
import sys
from network_utils import resolveClientIp

try:
    import tagilmo.utils.mission_builder as mb
    from tagilmo.utils.vereya_wrapper import MCConnector, RobustObserver

except ImportError:
    print("Error: 'tagilmo' library not found.")
    print("Run: pip install git+https://github.com/trueagi-io/minecraft-demo.git")
    sys.exit(1)

def main():
    obs = mb.Observations()
    agentHandlers = mb.AgentHandlers(observations=obs)
    
    miss = mb.MissionXML(agentSections=[
        mb.AgentSection(name='PythonPlayer', agenthandlers=agentHandlers)
    ])
    
    world = mb.defaultworld(seed='12345')
    miss.setWorld(world)
    
    
    miss.serverSection.initial_conditions.allowedmobs = "Pig Sheep Cow"
    miss.serverSection.initial_conditions.time_pass = 'false'
    miss.serverSection.initial_conditions.time_start = "1000"


    print("Connecting to Minecraft")

    client_ip = resolveClientIp()
    mc = MCConnector(miss, clientIp=client_ip) 
    rob = RobustObserver(mc)


    try:
        mc.safeStart()
    except Exception as e:
        print(f"Failed to start mission: {e}")
        return

    print("Mission accepted. Waiting for spawn ...")
    time.sleep(2)

    try:
        print("\nTesting")
        
        print("Moving Forward")
        rob.sendCommand('move 1')
        time.sleep(10)
        rob.sendCommand('move 0')
        
        print("Turning")
        rob.sendCommand('turn 0.5')
        time.sleep(1)
        rob.sendCommand('turn 0')
        
        print("Jumping")
        rob.sendCommand('jump 1')
        time.sleep(1)
        rob.sendCommand('jump 0')

    except KeyboardInterrupt:
        print("Stopping ...")
    finally:
        rob.sendCommand('move 0')
        rob.sendCommand('turn 0')
        print("Test finished.")

if __name__ == "__main__":
    main()