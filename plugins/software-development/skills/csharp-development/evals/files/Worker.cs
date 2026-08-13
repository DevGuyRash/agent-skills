using System;

static class Worker
{
    public static void Run(Action operation, Action<Exception> log)
    {
        try { operation(); }
        catch (Exception ex)
        {
            log(ex);
            throw ex;
        }
    }
}
