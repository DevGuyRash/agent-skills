def map_jobs(jobs, worker_count: 3, queue_capacity: 2, &operation)
  queue = Thread::Queue.new
  workers = worker_count.times.map do
    Thread.new do
      loop do
        job = queue.pop
        break if job.nil?
        operation.call(job)
      end
    end
  end

  jobs.each { |job| queue << job }
  worker_count.times { queue << nil }
  workers.map(&:join)
end
