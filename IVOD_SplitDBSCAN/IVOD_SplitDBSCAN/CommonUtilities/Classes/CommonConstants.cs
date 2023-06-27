using CommonUtilities.Helpers;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CommonUtilities.Classes
{
    public static class Constants
    {
        public const string GeneralConfig = "Configs\\general.json";
        public const string CPFServiceID = "TPN_SNT_CPF";
        public const string GSServiceID = "TPN_SNT_GS";
        public const string PALServiceID = "TPN_SNT_PAL";
    }

    public static class CommandID
    {
        // Passport
        public static readonly int StartPassportCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "startPassportCapture", 3001, Constants.GeneralConfig);
        public static readonly int DeactivatePassportCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "deactivatePassportReader", 3002, Constants.GeneralConfig);

        // Faceiris
        public static readonly int StartCaptureIrisOnlyEntry = Utilities.GetConfigurationWithPath("$.CommandIDs", "startCaptureIris_Entry", 5000, Constants.GeneralConfig);
        public static readonly int StartCaptureFaceIrisEntry = Utilities.GetConfigurationWithPath("$.CommandIDs", "startCaptureFaceIris_Entry", 5001, Constants.GeneralConfig);
        public static readonly int StopCaptureEntry = Utilities.GetConfigurationWithPath("$.CommandIDs", "stopCaptureFaceIris_Entry", 5002, Constants.GeneralConfig);
        public static readonly int StartCaptureFaceOnlyEntry = Utilities.GetConfigurationWithPath("$.CommandIDs", "startCaptureFace_Entry", 5003, Constants.GeneralConfig);
        public static readonly int EnableStreamEntry = Utilities.GetConfigurationWithPath("$.CommandIDs", "startStream_Entry", 5004, Constants.GeneralConfig);
        public static readonly int DisableStreamEntry = Utilities.GetConfigurationWithPath("$.CommandIDs", "stopStream_Entry", 5005, Constants.GeneralConfig);
        public static readonly int EnableApproachEntry = Utilities.GetConfigurationWithPath("$.CommandIDs", "startApproachDetect_Entry", 5006, Constants.GeneralConfig);
        public static readonly int DisableApproachEntry = Utilities.GetConfigurationWithPath("$.CommandIDs", "stopApproachDetect_Entry", 5007, Constants.GeneralConfig);

        public static readonly int StartCaptureIrisOnlyMantrap = Utilities.GetConfigurationWithPath("$.CommandIDs", "startCaptureIris_Mantrap", 5500, Constants.GeneralConfig);
        public static readonly int StartCaptureFaceIrisMantrap = Utilities.GetConfigurationWithPath("$.CommandIDs", "startCaptureFaceIris_Mantrap", 5501, Constants.GeneralConfig);
        public static readonly int StopCaptureMantrap = Utilities.GetConfigurationWithPath("$.CommandIDs", "stopCaptureFaceIris_Mantrap", 5502, Constants.GeneralConfig);
        public static readonly int StartCaptureFaceOnlyMantrap = Utilities.GetConfigurationWithPath("$.CommandIDs", "startCaptureFace_Mantrap", 5503, Constants.GeneralConfig);
        public static readonly int EnableStreamMantrap = Utilities.GetConfigurationWithPath("$.CommandIDs", "startStream_Mantrap", 5504, Constants.GeneralConfig);
        public static readonly int DisableStreamMantrap = Utilities.GetConfigurationWithPath("$.CommandIDs", "stopStream_Mantrap", 5505, Constants.GeneralConfig);
        public static readonly int EnableApproachMantrap = Utilities.GetConfigurationWithPath("$.CommandIDs", "startApproachDetect_Mantrap", 5506, Constants.GeneralConfig);
        public static readonly int DisableApproachMantrap = Utilities.GetConfigurationWithPath("$.CommandIDs", "stopApproachDetect_Mantrap", 5507, Constants.GeneralConfig);

        public static readonly int StartKioskCapture = StartCaptureFaceIrisMantrap;
        public static readonly int StartKioskFaceCapture = StartCaptureFaceOnlyMantrap;
        public static readonly int StartKioskIrisCapture = StartCaptureIrisOnlyMantrap;

        // Fingerprint
        public readonly static int LeftThumbCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "leftThumbCapture", 4010, Constants.GeneralConfig);
        public readonly static int LeftIndexCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "leftIndexCapture", 4011, Constants.GeneralConfig);
        public readonly static int LeftMiddleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "leftMiddleCapture", 4012, Constants.GeneralConfig);
        public readonly static int LeftRingCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "leftRingCapture", 4013, Constants.GeneralConfig);
        public readonly static int LeftLittleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "leftLittleCapture", 4014, Constants.GeneralConfig);
        public readonly static int rightThumbCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rightThumbCapture", 4015, Constants.GeneralConfig);
        public readonly static int rightIndexCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rightIndexCapture", 4016, Constants.GeneralConfig);
        public readonly static int rightMiddleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rightMiddleCapture", 4017, Constants.GeneralConfig);
        public readonly static int rightRingCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rightRingCapture", 4018, Constants.GeneralConfig);
        public readonly static int rightLittleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rightLittleCapture", 4019, Constants.GeneralConfig);
        public readonly static int LeftFourCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "leftFourCapture", 4020, Constants.GeneralConfig);
        public readonly static int RightFourCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rightFourCapture", 4021, Constants.GeneralConfig);
        public readonly static int TwoThumbCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "twoThumbsCapture", 4022, Constants.GeneralConfig);
        public readonly static int TwoIndexCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "twoIndexCapture", 4023, Constants.GeneralConfig);
        public readonly static int RightIndexMiddleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rightIndexMiddleCapture", 4024, Constants.GeneralConfig);
        public readonly static int RightRingLittleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rightRingLittleCapture", 4025, Constants.GeneralConfig);
        public readonly static int LeftIndexMiddleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "leftIndexMiddleCapture", 4026, Constants.GeneralConfig);
        public readonly static int LeftRingLittleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "leftRingLittleCapture", 4027, Constants.GeneralConfig);
        public readonly static int RollRightThumbCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rollRightThumbCapture", 4028, Constants.GeneralConfig);
        public readonly static int RollRightIndexCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rollRightIndexCapture", 4029, Constants.GeneralConfig);
        public readonly static int RollRightMiddleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rollRightMiddleCapture", 4030, Constants.GeneralConfig);
        public readonly static int RollRightRightCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rollRightRightCapture", 4031, Constants.GeneralConfig);
        public readonly static int RollRightLittleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rollRightLittleCapture", 4032, Constants.GeneralConfig);
        public readonly static int RollLeftThumbCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rollLeftThumbCapture", 4033, Constants.GeneralConfig);
        public readonly static int RollLeftIndexCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rollLeftIndexCapture", 4034, Constants.GeneralConfig);
        public readonly static int RollLeftMiddleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rollLeftMiddleCapture", 4035, Constants.GeneralConfig);
        public readonly static int RollLeftLeftCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rollLeftLeftCapture", 4036, Constants.GeneralConfig);
        public readonly static int RollLeftLittleCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "rollLeftLittleCapture", 4037, Constants.GeneralConfig);
        public readonly static int Id1DocumentCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "id1DocumentCapture", 4038, Constants.GeneralConfig);
        public readonly static int FPStopCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "deactivateFingerprintReader", 4002, Constants.GeneralConfig);
        public readonly static int FPStartStream = Utilities.GetConfigurationWithPath("$.CommandIDs", "startStreamFingerPrint", 4003, Constants.GeneralConfig);
        public readonly static int FPStopStream = Utilities.GetConfigurationWithPath("$.CommandIDs", "stopStreamFingerPrint", 4004, Constants.GeneralConfig);
        public readonly static int StopSignatureCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "stopSignatureCapture", 4100, Constants.GeneralConfig);
        public readonly static int StartSignatureCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "startSignatureCapture", 4101, Constants.GeneralConfig);
        public readonly static int ResetSignatureCapture = Utilities.GetConfigurationWithPath("$.CommandIDs", "resetSignatureCapture", 4102, Constants.GeneralConfig);


        public readonly static int SwitchDirectionA = Utilities.GetConfigurationWithPath("$.CommandIDs", "direction_A", 9901, Constants.GeneralConfig);
        public readonly static int SwitchDirectionB = Utilities.GetConfigurationWithPath("$.CommandIDs", "direction_B", 9902, Constants.GeneralConfig);

        // Barcode
        public readonly static int StartBarcode = Utilities.GetConfigurationWithPath("$.CommandIDs", "startBarcodeCapture", 6001, Constants.GeneralConfig);
        public readonly static int StopBarcode = Utilities.GetConfigurationWithPath("$.CommandIDs", "stopBarcodeCapture", 6003, Constants.GeneralConfig); 
        
        // PeopleCount 
        public readonly static int StartPeopleCount = Utilities.GetConfigurationWithPath("$.CommandIDs", "startPeopleCount", 2541, Constants.GeneralConfig);
        public readonly static int StopPeopleCount = Utilities.GetConfigurationWithPath("$.CommandIDs", "stopPeopleCount", 2542, Constants.GeneralConfig);
    }

    public static class EventID
    {
        // Passport
        public static int STARTPASSPORTCAPTURE = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='startPassportCapture')].Event.ID", "", 1100, Constants.GeneralConfig);
        public static int PASSPORTCAPTURESUCCEED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='passportCaptureSucceed')].Event.ID", "", 1110, Constants.GeneralConfig);
        public static int PASSPORTCAPTUREFAILED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='passportCaptureFailed')].Event.ID", "", 1121, Constants.GeneralConfig);
        public static int PASSPORTREACHEDMAXATTEMPTS = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='passportReachedMaxAttempts')].Event.ID", "", 1122, Constants.GeneralConfig);
        public static int FORGEDPASSPORT = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='forgedPassport')].Event.ID", "", 1123, Constants.GeneralConfig);
        public static int PASSPORTDETECTED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='passportDetected')].Event.ID", "", 1151, Constants.GeneralConfig);
        public static int PASSPORTCAPTURECOMPLETED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='passportCaptureCompleted')].Event.ID", "", 1152, Constants.GeneralConfig);
        public static int PASSPORTREMOVED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='passportRemoved')].Event.ID", "", 1153, Constants.GeneralConfig);
        public static int PASSPORTCAPTURETIMEOUT = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='passportCaptureTimeOut')].Event.ID", "", 1154, Constants.GeneralConfig);
        public static int PASSPORTMRZCOMPLETED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='passportMRZCompleted')].Event.ID", "", 1155, Constants.GeneralConfig);
        public static int PASSPORTDATAPAGECOMPLETED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='passportDataPageCompleted')].Event.ID", "", 1156, Constants.GeneralConfig);
        public static int BARCODEDATARECEIVED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='barcodeDataReceived')].Event.ID", "", 1160, Constants.GeneralConfig);

        // Faceiris
        public static readonly int APPROACHDETECTED_ENTRY = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='approachDetected_Entry')].Event.ID", "", 1501, Constants.GeneralConfig); // cpf
        public static readonly int APPROACHDETECTED_MANTRAP = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='approachDetected_Mantrap')].Event.ID", "", 1502, Constants.GeneralConfig); // cpf
        public static readonly int FACEIRISCAPTURING = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='faceIrisCapturing')].Event.ID", "", 1500, Constants.GeneralConfig); // ecq
        public static readonly int FACEIRISCAPTURESUCCEED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='faceIrisCaptureSucceed')].Event.ID", "", 1510, Constants.GeneralConfig); // ecq
        public static readonly int FACEIRISCAPTUREFAILED_MANTRAP = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='faceIrisCaptureFailed_Mantrap')].Event.ID", "", 1521, Constants.GeneralConfig); // ecq, cpf
        public static readonly int FACECAPTUREREACHEDMAXRETRY = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='faceCaptureReachedMaxRetry')].Event.ID", "", 1522, Constants.GeneralConfig); // ecq
        public static readonly int FACEIRISCAPTUREREACHEDMAXRETRY = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='faceIrisCaptureReachedMaxRetry')].Event.ID", "", 1523, Constants.GeneralConfig); // ecq
        public static readonly int FAKEFACEDETECTED_MANTRAP = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fakeFaceDetected_Mantrap')].Event.ID", "", 1524, Constants.GeneralConfig); // ecq, cpf
        public static readonly int FAKEIRISDETECTED_MANTRAP = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fakeIrisDetected_Mantrap')].Event.ID", "", 1525, Constants.GeneralConfig); // ecq, cpf
        public static readonly int FACEIRISFAILEDDETECT_MANTRAP = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='faceIrisFailedDetect_Mantrap')].Event.ID", "", 1526, Constants.GeneralConfig); // ecq, cpf
        public static readonly int FACEMATCHFAILED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='faceMatchFailed')].Event.ID", "", 1527, Constants.GeneralConfig); // ecq
        public static readonly int FACEIRISCAPTUREDFAILED_ENTRY = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='faceIrisCapturedFailed_Entry')].Event.ID", "", 1528, Constants.GeneralConfig); // ecq, cpf
        public static readonly int FAKEFACEDETECTED_ENTRY = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fakeFaceDetected_Entry')].Event.ID", "", 1529, Constants.GeneralConfig); // ecq, cpf
        public static readonly int FAKEIRISDETECTED_ENTRY = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fakeIrisDetected_Entry')].Event.ID", "", 1530, Constants.GeneralConfig); // ecq, cpf
        public static readonly int FACEIRISFAILEDDETECT_ENTRY = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='faceIrisFailedDetect_Entry')].Event.ID", "", 1531, Constants.GeneralConfig); // ecq, cpf
        public static readonly int FACECAPTURECOMPLETED_ENTRY = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='faceCaptureCompleted_Entry')].Event.ID", "", 1552, Constants.GeneralConfig); // ecq, cpf
        public static readonly int FACECAPTURECOMPLETED_MANTRAP = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='faceCaptureCompleted_Mantrap')].Event.ID", "", 1553, Constants.GeneralConfig); // ecq, cpf

        // Fingerprint
        public static readonly int FINGERPRINTCAPTURING = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fingerprintCapturing')].Event.ID", "", 1400, Constants.GeneralConfig);
        public static readonly int FINGERPRINTCAPTURESUCCEED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fingerprintCaptureSucceed')].Event.ID", "", 1410, Constants.GeneralConfig);
        public static readonly int FINGERPRINTCAPTUREFAILED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fingerprintCaptureFailed')].Event.ID", "", 1421, Constants.GeneralConfig);
        public static readonly int FINGRPINTCAPTUREREACHEDMAXRETRY = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fingrpintCaptureReachedMaxRetry')].Event.ID", "", 1422, Constants.GeneralConfig);
        public static readonly int FINGERPRINTFAILEDDETECT = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fingerprintFailedDetect')].Event.ID", "", 1424, Constants.GeneralConfig);
        public static readonly int FINGERPRINTDISCONNECTED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fingerprintDisconnected')].Event.ID", "", 1450, Constants.GeneralConfig);
        public static readonly int FINGERPRINTCAPTURECOMPLETED = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fingerprintCaptureCompleted')].Event.ID", "", 1452, Constants.GeneralConfig);
        public static readonly int FINGERPRINTCAPTUREFAILURE = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fingerprintCaptureFailure')].Event.ID", "", 1453, Constants.GeneralConfig);
        public static readonly int FINGERPRINTPREVIEWIMAGE = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='fingerprintPreviewImage')].Event.ID", "", 1454, Constants.GeneralConfig);

        // Heartbeat
        public static readonly int WORKFLOWINVALIDLICENSE = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='wfInvalidLicense')].Event.ID", "", 8887, Constants.GeneralConfig);
        public static readonly int WORKFLOWHEARTBEAT = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='wfHeartbeat')].Event.ID", "", 8888, Constants.GeneralConfig);
        public static readonly int CPFINVALIDLICENSE = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='cpfInvalidLicense')].Event.ID", "", 8889, Constants.GeneralConfig);
        public static readonly int PALINVALIDLICENSE = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='palInvalidLicense')].Event.ID", "", 8890, Constants.GeneralConfig);
        public static readonly int GSINVALIDLICENSE = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='gsInvalidLicense')].Event.ID", "", 8891, Constants.GeneralConfig);
        public static readonly int GSHEARTBEAT = Utilities.GetConfigurationWithPath("$.EventIDs[?(@.Event.Name=='gsHeartbeat')].Event.ID", "", 8892, Constants.GeneralConfig);
    }
}
