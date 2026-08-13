def run_job(database, command)
  database.begin_transaction
  child = Process.spawn(command)
  yield
rescue Exception => error
  warn error.message
end
