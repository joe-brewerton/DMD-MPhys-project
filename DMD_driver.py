import numpy as np
import importlib.util
if importlib.util.find_spec("ajiledriver") is not None:
    import ajiledriver as aj
else:
    print("Warning: ajiledriver not found. Using mock driver.")
    import ajile_mock_driver as aj
from warnings import warn
from typing import Union
# Set up logging
import logging
logger = logging.getLogger(__name__)


class DMD_driver:
    """Class defined to wrap Ajile DMD controller."""
    # Constants
    HEIGHT: int = aj.DMD_IMAGE_HEIGHT_MAX
    WIDTH: int = aj.DMD_IMAGE_WIDTH_MAX
    # Hardware connection
    _system = None
    _project = None
    _sequence = None
    _frames = None
    # Configuration
    dmd_index: int = None
    project_name: str = "default"
    main_sequence_ID: int = 1
    total_frames: int = 0
    # Variables
    frame_time: int = 10

    def __init__(self, comm_interface=None,
                 ipaddress: Union[str, None] = "192.168.200.1",
                 port: Union[int, None] = 5005) -> None:
        """connects to DMD"""
        # Set up interface
        if comm_interface is None:
            comm_interface = aj.USB3_INTERFACE_TYPE
        # Create host system
        logger.debug("Creating host system")
        self._system = aj.HostSystem()
        # Set connection settings
        logger.debug("Setting connection settings")
        self._system.SetConnectionSettingsStr(ipaddress, "255.255.255.0", "0.0.0.0", port)

        # Set interface
        logger.debug("Setting communication interface")
        self._system.SetCommunicationInterface(comm_interface)
        # Set USB number
        logger.debug("Setting USB number")
        self._system.SetUSB3DeviceNumber(0)
        # Check if the system can be started
        if self._system.StartSystem() != aj.ERROR_NONE:
            raise IOError("Error starting AjileSystem")

    def create_project(self, project_name: Union[str, None] = "default"):
        """
        create_project(project_name)
        Creates a project object and adds components to it

        args:
            project_name: name of the project

        """
        if self._project is not None:
            warn("Project already exists. Using existing project.", UserWarning)
            return self._project
        # create a project object
        logger.debug(f"Creating project {project_name}")
        self._project = aj.Project(project_name)
        # add system hardware components to project
        logger.debug("Adding components to project")
        self._project.SetComponents(self._system.GetProject().Components())
        # Get DMD index from the project components
        logger.debug("Getting DMD index")
        self.dmd_index = self._project.GetComponentIndexWithDeviceType(aj.DMD_4500_DEVICE_TYPE)
        return self._project

    def create_main_sequence(self, seq_rep_count: int):
        """Creates a sequence, sequence item and frame object

        args:
            seq_rep_count: number of times the sequence should be repeated"""

        if self._project is None:
            raise SystemError("Project must be created before sequence is created")
# Create the sequence
        """
        taken from C# driver to understand the meaning of each arg
        Sequence(ushort sequenceID, 
                    string sequenceName, 
                    DeviceType_e hardwareType, 
                    SequenceType_e sequenceType, 
                    uint sequenceRepeatCount)
        SequenceType_e:
            SEQ_TYPE_PRELOAD = 0,
            SEQ_TYPE_STREAM = 1
        """
        # Create sequence
        logger.debug("Creating sequence")
        seq = aj.Sequence(
            self.main_sequence_ID,
            self.project_name + str(self.main_sequence_ID),
            aj.DMD_4500_DEVICE_TYPE,
            aj.SEQ_TYPE_PRELOAD,
            seq_rep_count
        )
        # Add the sequence to the project
        logger.debug("Adding sequence to project")
        self._project.AddSequence(seq)
        # Check sequence has been uploaded
        logger.debug("Checking sequence has been uploaded")
        _, sequence_was_found = self._project.FindSequence(self.main_sequence_ID)
        if not sequence_was_found:
            raise IOError('Sequence not found on device after adding.')
        # Return sequence
        return self._sequence

    def add_sequence_item(self, image: np.array, seq_id: int, frame_time: int = 1000):
        """
        add_sub_sequence(image, seqID, frameTime)
        Add a subsequence - in our case, a single frame - to the main sequence

        arg:
            image: np.array image
            seqID: - ID of the sequence, starts with 1 and is incremented by 1
            frameTime: - frame time in milliseconds
        """
        # Create a sequence item based on C signature
        # "public SequenceItem(ushort sequenceID, uint sequenceItemRepeatCount)"
        self.total_frames += 1
        logger.debug("Creating sequence item")
        seq_item = aj.SequenceItem(seq_id, 1)

        # Add sequence item to the project
        logger.debug("Adding sequence item to project")
        self._project.AddSequenceItem(seq_item)

        # create two frames and add them to the project
        # (added to the last sequence item in the sequence)
        image_id = self.total_frames + 1
        logger.debug("Creating Image")
        aj_image = aj.Image(image_id)
        
        # load the NumPy image into the Image object and convert it to DMD 4500 format
        logger.debug("Loading image from memory")
        aj_image.ReadFromMemory(image, 8, aj.ROW_MAJOR_ORDER, aj.DMD_4500_DEVICE_TYPE)

        # Add image to the project
        logger.debug("Adding image to project")
        self._project.AddImage(aj_image)

        # Define frame related to an image
        logger.debug("Creating frame")
        frame = aj.Frame()
        frame.SetSequenceID(seq_id)
        logger.debug("Setting frame properties")
        frame.SetImageID(image_id)
        logger.debug("Setting frame time")
        frame.SetFrameTimeMSec(int(frame_time))
        logger.debug("Adding frame to project")
        self._project.AddFrame(frame)
        
    def create_trigger_rules(self, controller_index: int,
                             trigger_on=aj.FRAME_STARTED,
                             trigger_output=aj.EXT_TRIGGER_OUTPUT_1) -> None:
        """Create a trigger rule to connect the DMD frame started to the external output trigger"""
        if self._project is None:
            raise IOError('Project must be defined before trigger is created')
        # Create trigger rule
        logger.debug("Creating trigger rule")
        rule = aj.TriggerRule()
        # Add trigger from device "TriggerRulePair(byte componentIndex, byte triggerType)"
        logger.debug("Adding trigger from device")
        rule.AddTriggerFromDevice(aj.TriggerRulePair(self.dmd_index, trigger_on))
        # Set trigger
        logger.debug("Setting trigger")
        rule.SetTriggerToDevice(aj.TriggerRulePair(controller_index, trigger_output))
        # add the trigger rule to the project
        logger.debug("Adding trigger rule to project")
        self._project.AddTriggerRule(rule)

    def my_trigger(self, controller_index: int = 0, trigger_duration: float = 1 / 32768):
        """Custom trigger rule

        This trigger rule is used to trigger the DMD from the PicoScope.
        """
        # Get current trigger settings
        input_trigger_settings = self._project.Components()[controller_index].InputTriggerSettings()
        output_trigger_settings = self._project.Components()[controller_index].OutputTriggerSettings()

        # Iterate over output trigger settings, and set these to rising edge, 1/32768
        for index in range(len(output_trigger_settings)):
            output_trigger_settings[index] = aj.ExternalTriggerSetting(
                aj.RISING_EDGE,
                aj.FromMSec(trigger_duration))
            input_trigger_settings[index] = aj.ExternalTriggerSetting(aj.RISING_EDGE)

        # Set trigger settings
        self._project.SetTriggerSettings(controller_index, input_trigger_settings, output_trigger_settings)

        # Create trigger rule
        dmd_frame_started_to_ext_trig_out = aj.TriggerRule()

        dmd_frame_started_to_ext_trig_out.AddTriggerFromDevice(
            aj.TriggerRulePair(self.dmd_index, aj.FRAME_STARTED))

        dmd_frame_started_to_ext_trig_out.SetTriggerToDevice(
            aj.TriggerRulePair(controller_index, aj.EXT_TRIGGER_OUTPUT_1))

        # add the trigger rule to the project
        self._project.AddTriggerRule(dmd_frame_started_to_ext_trig_out)

    def stop_projecting(self) -> None:
        """Stop projecting"""
        logger.debug("Stopping projection")
        self._system.GetDriver().StopSequence(self.dmd_index)

    def start_projecting(self, reporting_freq: int = 1) -> None:
        """
        start_projecting(reporting_freq)

        Load project, and start sequence

        args:
            reportingFreq: reporting frequency (must be greater than 0)
        """
        logger.debug("Loading project")
        self._system.GetDriver().LoadProject(self._project)
        # Wait for load to complete
        self._system.GetDriver().WaitForLoadComplete(-1)
        # Start the current sequence
        # StartSequence(uint sequenceID, int deviceID, uint reportingFreq=1)
        logger.debug(f'Starting sequence - {self.main_sequence_ID}, {self.dmd_index}')
        self._system.GetDriver().StartSequence(self.main_sequence_ID, self.dmd_index, 5)
        # Wait to start running
        while self._system.GetDeviceState(self.dmd_index).RunState() != aj.RUN_STATE_RUNNING:
            pass

    @property
    def project(self):
        return self._project

    @property
    def system(self):
        return self._system

    @property
    def sequence(self):
        return self._sequence


if __name__ == "__main__":
    dmd = DMD_driver()