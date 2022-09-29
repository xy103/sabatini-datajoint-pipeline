import datajoint as dj
from element_animal import subject
from element_lab import lab
from element_session import session_with_id as session

from workflow import db_prefix

__all__ = ["lab", "subject", "session"]

# ------------- Activate "lab" schema -------------
lab.activate(db_prefix + "lab")

Source = lab.Source
Lab = lab.Lab
Protocol = lab.Protocol
User = lab.User
Location = lab.Location
Project = lab.Project

# ------------- Activate "subject" schema -------------
subject.activate(db_prefix + "subject", linking_module=__name__)
Subject = subject.Subject

Experimenter = lab.User

# ------------- Activate "session" schema -------------
session.activate(db_prefix + "session", linking_module=__name__)


# Declare BrainCoordinateReference table for use in element-array-ephys
@lab.schema
class BrainCoordinateReference(dj.Lookup):
    definition = """
    reference   : varchar(60)
    """
    contents = zip(
        ["bregma", "lambda", "dura", "skull_surface", "sagittal_suture", "sinus"]
    )


lab.BrainCoordinateReference = BrainCoordinateReference

# Declare Equipment table for use in element_calcium_imaging
@lab.schema
class Equipment(dj.Lookup):
    definition = """
    scanner: varchar(32)
    """
    contents = zip(["Nikon A1 plus"])


lab.Equipment = Equipment

# Declare Device table for use in element_deeplabcut
@lab.schema
class Device(dj.Lookup):
    definition = """
    device_id           : smallint
    ---
    device_name         : varchar(32)  # user-friendly name of the device
    device_description  : varchar(256)
    """


lab.Device = Device


@lab.schema
class Virus(dj.Lookup):
    definition = """            
    name                : varchar(32)  # (e.g., AAV9-DIO-GCaMP6s)
    ---
    notes=''            : varchar(64)  
    """


lab.Virus = Virus


@lab.schema
class BrainRegion(dj.Manual):
    definition = """
    region_name: varchar(128)
    ---
    acronym='' : varchar(32)
    """


lab.BrainRegion = BrainRegion


@lab.schema
class Hemisphere(dj.Lookup):
    definition = """
    hemisphere: varchar(8)
    """

    contents = zip(["left", "right", "middle"])


lab.Hemisphere = Hemisphere


@lab.schema
class ImplantationType(dj.Lookup):
    definition = """
    implant_type: varchar(16)
    """

    contents = zip(["ephys", "fiber"])


lab.ImplantationType = ImplantationType


@subject.schema
class VirusInjection(dj.Manual):
    definition = """
    -> subject.Subject
    injection_id            : tinyint unsigned
    ---
    -> lab.Virus
    -> lab.User
    injection_volume        : float                         # injection volume
    injection_time=null     : datetime                      # injection time
    rate_of_injection=null  : float                         # rate of injection
    wait_time=null          : float                         # wait time after injection (in min)
    -> lab.BrainRegion.proj(brain_region='region_name')    # targeted brain region
    -> Hemisphere
    notes=''                : varchar(1000)
    """

    class Coordinate(dj.Part):
        definition = """
        -> master
        ---
        ap            : decimal(6, 3)           # (um) anterior-posterior; ref is 0
        -> lab.BrainCoordinateReference.proj(ap_ref='reference')
        ml            : decimal(6, 3)           # (um) medial axis; ref is 0 
        -> lab.BrainCoordinateReference.proj(ml_ref='reference')
        dv            : decimal(6, 3)           # (um) dorso-ventral axis; ref is 0; more ventral is more negative
        -> lab.BrainCoordinateReference.proj(dv_ref='reference')
        theta=null    : decimal(6, 3)           # (deg) rotation about the ml-axis [0, 180] - w.r.t the z+ axis
        phi=null      : decimal(6, 3)           # (deg) rotation about the dv-axis [0, 360] - w.r.t the x+ axis
        beta=null     : decimal(6, 3)           # (deg) rotation about the shank [-180, 180] - clockwise is increasing in degree - 0 is the probe-front facing anterior
        """


subject.VirusInjection = VirusInjection


@subject.schema
class Perfusion(dj.Manual):
    definition = """
    -> subject.Subject
    ---
    -> lab.User.proj(experimenter='user')  # person who performed perfusion
    date                : date          # perfusion date
    reagent             : varchar(16)   # (e.g., PFA)
    """


subject.Perfusion = Perfusion


@subject.schema
class Implantation(dj.Manual):
    definition = """
    -> subject.Subject
    implant_date  : date   # surgery date
    -> lab.ImplantationType
    -> lab.BrainRegion.proj(brain_region='region_name')
    -> lab.Hemisphere
    ---
    -> lab.User.proj(surgeon='user')        # surgeon
    ap            : decimal(6, 3)           # (um) anterior-posterior; ref is 0
    -> lab.BrainCoordinateReference.proj(ap_ref='reference')
    ml            : decimal(6, 3)           # (um) medial axis; ref is 0 
    -> lab.BrainCoordinateReference.proj(ml_ref='reference')
    dv            : decimal(6, 3)           # (um) dorso-ventral axis; ref is 0; more ventral is more negative
    -> lab.BrainCoordinateReference.proj(dv_ref='reference')
    theta=null    : decimal(6, 3)           # (deg) rotation about the ml-axis [0, 180] - w.r.t the z+ axis
    phi=null      : decimal(6, 3)           # (deg) rotation about the dv-axis [0, 360] - w.r.t the x+ axis
    beta=null     : decimal(6, 3)           # (deg) rotation about the shank [-180, 180] - clockwise is increasing in degree - 0 is the probe-front facing anterior
    """


subject.Implantation = Implantation