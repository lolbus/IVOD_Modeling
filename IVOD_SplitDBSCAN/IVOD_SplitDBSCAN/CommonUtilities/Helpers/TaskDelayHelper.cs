using System.Threading;
using System.Threading.Tasks;

namespace CommonUtilities.Helpers
{
    public class TaskDelayHelper
    {
        private CancellationTokenSource source;

        public TaskDelayHelper() { source = new(); }
        private bool _isDelay;

        public async Task<bool> Delay(int i, int millsecondsBeforeCancel = 0)
        {
            bool isComplete;

            try
            {
                _isDelay = true;
                if (source == null) source = new();
                if (millsecondsBeforeCancel > 0) _ = DelayCancel(millsecondsBeforeCancel);
                await Task.Delay(i, source.Token);
                isComplete = true;
            }
            catch (TaskCanceledException)
            {
                // Cancelled manually
                isComplete = false;
            }
            finally
            {
                if (source != null)
                {
                    source.Dispose();
                    source = null;
                }
                _isDelay = false;
            }

            return isComplete;
        }

        private async Task DelayCancel(int milliseconds)
        {
            await Task.Delay(milliseconds).ContinueWith(task =>
            {
                Cancel();
            });
        }

        public bool Cancel()
        {
            if (source == null) return false;

            source.Cancel();
            return true;
        }

        public bool isDelay()
            => _isDelay;
    }
}
