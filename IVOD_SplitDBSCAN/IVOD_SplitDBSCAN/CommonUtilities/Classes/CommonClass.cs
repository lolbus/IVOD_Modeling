using CommonUtilities.Constants;
using CommonUtilities.Helpers;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CommonUtilities.Classes
{
    public class License
    {
        public License(long seconds, int licResponseDtIntervalSec)
        {
            _seconds = seconds;
            _licResponseDtIntervalSec = licResponseDtIntervalSec;
            status = LicenseStatus.Activated;
            _lastUpdateTime = DateTime.Now.ToEpochTime();
        }

        // private
        private long _lastUpdateTime = DateTime.MinValue.ToEpochTime();
        private uint _invalidRespDtCount = 0;
        private int _licResponseDtIntervalSec = 0;
        private long _seconds = 0;

        // public
        public LicenseStatus status { get; set; } = LicenseStatus.Deactivated;
        public long lastUpdateTime
        {
            get => _lastUpdateTime;
            set
            {
                var nowDt = DateTime.Now.ToEpochTime();
                if (((nowDt - value) >= -_licResponseDtIntervalSec) &&
                    ((nowDt - value) <= _licResponseDtIntervalSec))
                {
                    _lastUpdateTime = value;
                    _invalidRespDtCount = 0;
                }
                else
                {
                    _invalidRespDtCount++;
                }
            }
        }
        public bool IsValid() => status == LicenseStatus.Activated && _invalidRespDtCount <= 3;
        public bool IsNotExpired() => DateTime.Now.ToEpochTime() - _lastUpdateTime <= _seconds;
        public void Deactivate()
        {

            status = LicenseStatus.Deactivated;
            _lastUpdateTime = DateTime.Now.ToEpochTime();
        }
        public override string ToString()
        {
            return $"License status: {status}, lastUpdateTime: {_lastUpdateTime.EpochTimeToDateTime()}, licValidIntervalSec: {_seconds}, invalidRespDtCount: {_invalidRespDtCount}";
        }
    }
}
