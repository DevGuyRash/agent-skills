<?php

final class Worker
{
    private $stream;

    public function run(PDO $database): void
    {
        $database->beginTransaction();
        $this->stream = fopen('php://temp', 'w+');
        try {
            process_job($this->stream);
        } catch (Throwable $error) {
            error_log($error->getMessage());
        }
    }

    public function __destruct()
    {
        if (is_resource($this->stream)) {
            fclose($this->stream);
        }
    }
}
