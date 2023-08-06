"""
Classes for creating a DICOM from scratch

Tom Roberts
"""

import datetime
import os
import pydicom as pyd
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.datadict import DicomDictionary, keyword_dict

nii2dcm_temp_filename = 'nii2dcm_tempfile.dcm'


class Dicom:
    """
    Creates basic DICOM structure

    Assumptions:
    - is_implicit_VR = False
    - is_little_endian = True
    - ImageOrientationPatient hard-coded

    """

    def __init__(self, filename=nii2dcm_temp_filename):

        self.filename = filename

        # TODO:
        #  - arrange tags according to NEMA DICOM modules, e.g. Patient, General Study, Image Pixel, etc. (use
        #  Innolitics DICOM Standard browser to guide)
        #  - possibly arrange tags into Series/Instance tags

        self.dcm_dictionary_update()

        # Instantiates minimal Pydicom FileMetaDataset object
        self.file_meta = FileMetaDataset()
        self.file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1'  # Explicit VR Little Endian
        self.file_meta.ImplementationVersionName = 'nii2dcm_DICOM'

        # Instantiates minimal DataSet object
        self.ds = FileDataset(filename, {}, file_meta=self.file_meta, preamble=b"\0" * 128)
        self.ds.is_implicit_VR = False
        self.ds.is_little_endian = True
        self.ds.SpecificCharacterSet = "ISO_IR 100"
        self.ds.ImageType = ['DERIVED', 'SECONDARY']
        self.ds.ProtocolName = "nii2dcm_DICOM"

        self.ds.PatientName = "Test^Firstname"
        self.ds.PatientID = "12345678"
        self.ds.AccessionNumber = "ABCXYZ"
        self.ds.PatientBirthDate = ""
        self.ds.PatientSex = ""
        self.ds.PatientAge = ""
        self.ds.PatientWeight = ""
        self.ds.BodyPartExamined = ""

        self.ds.InstitutionName = "INSTITUTION_NAME_NONE"
        self.ds.Manufacturer = ""
        self.ds.ManufacturerModelName = ""
        self.ds.StudyDescription = ''
        self.ds.InstanceCreatorUID = ''
        self.ds.SoftwareVersions = ''

        self.ds.SOPClassUID = ''  # initiated, should be defined by subclass
        self.ds.Modality = ''  # initiated, should be defined by subclass

        dt = datetime.datetime.now()
        dateStr = dt.strftime('%Y%m%d')
        timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds

        self.ds.ContentDate = dateStr
        self.ds.ContentTime = timeStr
        self.ds.StudyDate = dateStr
        self.ds.StudyTime = timeStr
        self.ds.SeriesDate = dateStr
        self.ds.SeriesTime = timeStr
        self.ds.AcquisitionDate = dateStr
        self.ds.AcquisitionTime = timeStr
        self.ds.InstanceCreationDate = dateStr
        self.ds.InstanceCreationTime = timeStr

        self.ds.Rows = ""
        self.ds.Columns = ""
        self.ds.PixelSpacing = ""
        self.ds.PixelRepresentation = ''
        self.ds.PatientPosition = ''
        self.ds.ImageOrientationPatient = ['1', '0', '0', '0', '1', '0']  # TODO: decide default

        self.ds.LossyImageCompression = ''

        self.ds.RescaleIntercept = ""
        self.ds.RescaleSlope = ""
        self.ds.WindowCenter = ""
        self.ds.WindowWidth = ""

        # per Instance tags
        self.ds.SOPInstanceUID = ""
        self.ds.InstanceNumber = ""
        self.ds.SliceThickness = ""
        self.ds.SpacingBetweenSlices = ""
        self.ds.SliceLocation = ""
        self.ds.ImagePositionPatient = ['0', '0', '0']

        self.init_study_tags()
        self.init_series_tags()

    def get_file_meta(self):
        return self.file_meta

    def get_dataset(self):
        return self.ds

    def save_as(self):
        print("Writing DICOM to", os.path.join(os.getcwd(), self.filename))
        self.ds.save_as(self.filename)

    def init_study_tags(self):
        """
        Create Study Tags
        - these tags are fixed across Instances and Series
        """

        # Possible per Study Tags
        # StudyInstanceUID

        self.ds.StudyInstanceUID = pyd.uid.generate_uid(None)

    def init_series_tags(self):
        """
        Create Series Tags
        - these tags are fixed across Instances
        """

        # Possible per Series Tags
        # SeriesInstanceUID
        # FrameOfReferenceUID
        # SeriesDate
        # SeriesTime
        # AcquisitionDate
        # AcquisitionTime
        # SeriesNumber

        self.ds.SeriesInstanceUID = pyd.uid.generate_uid(None)
        self.ds.FrameOfReferenceUID = pyd.uid.generate_uid(None)
        self.ds.SeriesNumber = ""
        self.ds.AcquisitionNumber = ""

    def dcm_dictionary_update(self):
        """
        Update Pydicom DicomDictionary object with non-standard Private tags. Note: these tags are not added to the
        instantiated nii2dcm Dicom object; the DicomDictionary object is just updated meaning that these tags are now
        available to be written if the user desires.

        Tuple definitions: (VR, VM, description, is_retired flag, keyword)

        See: https://pydicom.github.io/pydicom/stable/auto_examples/metadata_processing/plot_add_dict_entries.html
        """

        new_dict_items = {
            0x20011002: ('IS', '1', "Chemical Shift Number MR", '', 'ChemicalShiftNumberMR'),
            0x20011008: ('IS', '1', "Phase Number", '', 'PhaseNumber'),
            0x2001100a: ('IS', '1', "Slice Number MR", '', 'SliceNumberMR'),
            0x2001100b: ('CS', '1', "Slice Orientation", '', 'SliceOrientation'),
            0x20011014: ('SL', '1', "Number Of Echoes", '', 'NumberOfEchoes'),
            0x20011015: ('SS', '1', "Number Of Locations", '', 'NumberOfLocations'),
            0x20011016: ('SS', '1', "Number Of PC Directions", '', 'NumberOfPCDirections'),
            0x20011017: ('SL', '1', "Number Of Phases MR", '', 'NumberOfPhasesMR'),
            0x20011018: ('SL', '1', "Number Of Slices MR", '', 'NumberOfSlicesMR'),
            0x20011020: ('LO', '1', "Scanning Technique", '', 'ScanningTechnique'),
            0x20011025: ('SH', '1', "Echo Time Display MR", '', 'EchoTimeDisplayMR'),
            0x20011060: ('SL', '1', "Number Of Stacks", '', 'NumberOfStacks'),
            0x20011063: ('CS', '1', "Examination Source", '', 'ExaminationSource'),
            # 0x2001107b: ('IS', '1', "Acquisition Number", '', 'AcquisitionNumber'), # Philips Private alternative
            0x20011081: ('IS', '1', "Number Of Dynamic Scans", '', 'NumberOfDynamicScans'),
            0x2001101a: ('FL', '3', "PC Velocity", '', 'PCVelocity'),
            0x2001101d: ('IS', '1', "Reconstruction Number MR", '', 'ReconstructionNumberMR'),
            0x20051035: ('CS', '1', '', '', 'unknowntag20051035'),
            # PIXEL --- this seems to also correspond to MRSeriesDataType?
            0x20051011: ('CS', '1', 'MR Image Type', '', 'MRImageType'),
            0x2005106e: ('CS', '1', 'MR Scan Sequence', '', 'MRScanSequence'),

            # Philips "Stack" Tags
            0x2001105f: ('SQ', '1', 'Stack', '', 'Stack'),
            0x20010010: ('LO', '1', "Private Creator", '', 'PrivateCreator20010010'),
            0x2001102d: ('SS', '1', 'StackNumberOfSlices', '', 'StackNumberOfSlices'),
            0x20011032: ('FL', '1', 'StackRadialAngle', '', 'StackRadialAngle'),
            0x20011033: ('CS', '1', 'StackRadialAxis', '', 'StackRadialAxis'),
            0x20011035: ('SS', '1', 'MRSeriesDataType', '', 'MRSeriesDataType'),  # SS - StackSliceNumber ?
            0x20011036: ('CS', '1', 'StackType', '', 'StackType'),
            0x20050010: ('LO', '1', 'Private Creator', '', 'PrivateCreator20050010'),
            # Is this duplicate necessary with entry above?
            0x20050011: ('LO', '1', 'Private Creator', '', 'PrivateCreator20050011'),
            0x20050012: ('LO', '1', 'Private Creator', '', 'PrivateCreator20050012'),
            0x20050013: ('LO', '1', 'Private Creator', '', 'PrivateCreator20050013'),
            0x20050014: ('LO', '1', 'Private Creator', '', 'PrivateCreator20050014'),
            0x20050015: ('LO', '1', 'Private Creator', '', 'PrivateCreator20050015'),
            0x20051071: ('FL', '1', 'MRStackAngulationAP', '', 'MRStackAngulationAP'),
            0x20051072: ('FL', '1', 'MRStackAngulationFH', '', 'MRStackAngulationFH'),
            0x20051073: ('FL', '1', 'MRStackAngulationRL', '', 'MRStackAngulationRL'),
            0x20051074: ('FL', '1', 'MRStackFovAP', '', 'MRStackFovAP'),
            0x20051075: ('FL', '1', 'MRStackFovFH', '', 'MRStackFovFH'),
            0x20051076: ('FL', '1', 'MRStackFovRL', '', 'MRStackFovRL'),
            0x20051078: ('FL', '1', 'MRStackOffcentreAP', '', 'MRStackOffcentreAP'),
            0x20051079: ('FL', '1', 'MRStackOffcentreFH', '', 'MRStackOffcentreFH'),
            0x2005107a: ('FL', '1', 'MRStackOffcentreRL', '', 'MRStackOffcentreRL'),
            0x2005107b: ('CS', '1', 'MRStackPreparationDirection', '', 'MRStackPreparationDirection'),
            0x2005107e: ('FL', '1', 'MRStackSliceDistance', '', 'MRStackSliceDistance'),
            0x20051081: ('CS', '1', 'MRStackViewAxis', '', 'MRStackViewAxis'),
            0x2005143c: ('FL', '1', 'MRStackTablePosLong', '', 'MRStackTablePosLong'),
            0x2005143d: ('FL', '1', 'MRStackTablePosLat', '', 'MRStackTablePosLat'),
            0x2005143e: ('FL', '1', 'MRStackPosteriorCoilPos', '', 'MRStackPosteriorCoilPos'),
            0x20051567: ('IS', '1', 'MRPhilipsX1', '', 'MRPhilipsX1'),

            # Phase Contrast/Velocity Tags
            0x00089209: ('CS', '1', "Acquisition Contrast", '', 'AcquisitionContrast'),
            0x00189014: ('CS', '1', "Phase Contrast", '', 'PhaseContrast'),
            0x00189090: ('FD', '3', "Velocity Encoding Direction", '', 'VelocityEncodingDirection'),
            0x00189091: ('FD', '1', "Velocity Encoding Minimum Value", '', 'VelocityEncodingMinimumValue'),
        }

        # Update the dictionary itself
        DicomDictionary.update(new_dict_items)

        # Update the reverse mapping from name to tag
        new_names_dict = dict([(val[4], tag) for tag, val in new_dict_items.items()])
        keyword_dict.update(new_names_dict)


class DicomMRI(Dicom):
    """
    Builds upon Dicom class by adding MR Image Module attributes

    The DICOM tags in this subclass make a minimal MR DICOM according to the NEMA DICOM standard, specifically
    the MR Image Module in section C.8.3:
    https://dicom.nema.org/medical/Dicom/current/output/chtml/part03/sect_C.8.3.html

    Tags labelled ":missing:" are defined in the NEMA MR standard, but not found in real DICOMs exported from an
    MR scanner
    """

    def __init__(self, filename=nii2dcm_temp_filename):
        super().__init__(filename)

        self.ds.Modality = 'MR'

        # MR Image Storage SOP Class
        # UID = 1.2.840.10008.5.1.4.1.1.4
        # https://dicom.nema.org/dicom/2013/output/chtml/part04/sect_I.4.html
        self.file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.4'
        self.ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.4'

        # ImageType
        # NEMA defines MR-specific ImageType terms here:
        # https://dicom.nema.org/medical/Dicom/current/output/chtml/part03/sect_C.8.3.html#sect_C.8.3.1.1.1
        # For now, will inherit from Dicom class
        self.ds.ImageType = self.ds.ImageType

        self.ds.SamplesPerPixel = ''

        # PhotometricInterpretation
        # TODO: decide MONOCHROME1 or MONOCHROME2 as default
        # https://dicom.nema.org/medical/Dicom/current/output/chtml/part03/sect_C.7.6.3.html#sect_C.7.6.3.1.2
        self.ds.PhotometricInterpretation = 'MONOCHROME2'

        # PresentationLUTShape
        # depends on PhotometricInterpretation: https://dicom.innolitics.com/ciods/mr-image/general-image/20500020
        if self.ds.PhotometricInterpretation == 'MONOCHROME2':
            self.ds.PresentationLUTShape = 'IDENTITY'
        elif self.ds.PhotometricInterpretation == 'MONOCHROME1':
            self.ds.PresentationLUTShape = 'INVERSE'

        # Bits Allocated
        # defined to equal 16 for MR Image Module
        # https://dicom.nema.org/medical/Dicom/current/output/chtml/part03/sect_C.8.3.html#sect_C.8.3.1.1.4
        self.ds.BitsAllocated = 16
        self.ds.BitsStored = ''  # TODO: determine if able to leave blank, or need to set = 12
        self.ds.HighBit = ''  # HighBit = BitsStored - 1

        self.ds.ScanningSequence = 'RM'  # :missing:, 'RM' = Research Mode
        self.ds.SequenceVariant = ''  # :missing:, TODO: set = 'NONE' ?
        self.ds.ScanOptions = ''  # :missing:
        self.ds.MRAcquisitionType = ''  # 2D or 3D
        self.ds.RepetitionTime = ''
        self.ds.EchoTime = ''
        self.ds.EchoTrainLength = ''
        self.ds.InversionTime = ''
        self.ds.TriggerTime = ''
        self.ds.SequenceName = ''
        self.ds.AngioFlag = ''  # :missing:
        self.ds.NumberOfAverages = ''
        self.ds.ImagingFrequency = ''
        self.ds.ImagedNucleus = ''
        self.ds.EchoNumbers = ''
        self.ds.MagneticFieldStrength = ''
        self.ds.NumberOfPhaseEncodingSteps = ''  # :missing:
        self.ds.PercentSampling = ''  # TODO set?
        self.ds.PercentPhaseFieldOfView = ''  # TODO set?
        self.ds.PixelBandwidth = ''
        self.ds.NominalInterval = ''  # :missing:
        self.ds.BeatRejectionFlag = ''  # :missing:
        self.ds.LowRRValue = ''  # :missing:
        self.ds.HighRRValue = ''  # :missing:
        self.ds.IntervalsAcquired = ''  # :missing:
        self.ds.IntervalsRejected = ''  # :missing:
        self.ds.PVCRejection = ''  # :missing:
        self.ds.SkipBeats = ''  # :missing:
        self.ds.HeartRate = ''
        self.ds.CardiacNumberOfImages = ''
        self.ds.TriggerWindow = ''
        self.ds.ReconstructionDiameter = ''  # :missing:
        self.ds.ReceiveCoilName = ''
        self.ds.TransmitCoilName = ''
        self.ds.AcquisitionMatrix = ''  # :missing:
        self.ds.InPlanePhaseEncodingDirection = ''  # ROW or COLUMN
        self.ds.FlipAngle = ''
        self.ds.SAR = ''
        self.ds.VariableFlipAngleFlag = ''  # :missing:
        self.ds.dBdt = ''
        self.ds.TemporalPositionIdentifier = ''  # :missing:
        self.ds.NumberOfTemporalPositions = ''
        self.ds.TemporalResolution = ''  # :missing:

        # Currently omitting, but part of NEMA MR Image module:
        # NEMA Table 10-7 “General Anatomy Optional Macro Attributes”

        # Currently omitting, but part of NEMA MR Image module:
        # NEMA Table 10-25 “Optional View and Slice Progression Direction Macro Attributes”

        self.ds.IsocenterPosition = ''  # :missing:
        self.ds.B1rms = ''


