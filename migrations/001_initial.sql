CREATE TABLE IF NOT EXISTS tasks (id uuid PRIMARY KEY, title varchar(240) NOT NULL, prompt text NOT NULL, tier varchar(16) NOT NULL, status varchar(32) NOT NULL DEFAULT 'pending', attempts integer NOT NULL DEFAULT 0, result jsonb, approval_id uuid, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS approvals (id uuid PRIMARY KEY, task_id uuid NOT NULL REFERENCES tasks(id), payload jsonb NOT NULL, payload_hash varchar(64) NOT NULL, status varchar(16) NOT NULL DEFAULT 'pending', expires_at timestamptz NOT NULL, decided_by varchar(128));
CREATE TABLE IF NOT EXISTS audit_events (id bigserial PRIMARY KEY, task_id uuid, event varchar(128) NOT NULL, data jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS approvals_task_status ON approvals(task_id,status);
CREATE INDEX IF NOT EXISTS tasks_status_created ON tasks(status,created_at);
