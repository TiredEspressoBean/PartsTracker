CREATE TABLE IF NOT EXISTS "django_migrations"
(
    "id"      integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
    "app"     varchar(255) NOT NULL,
    "name"    varchar(255) NOT NULL,
    "applied" datetime     NOT NULL
);
CREATE TABLE sqlite_sequence
(
    name,
    seq
);
CREATE TABLE IF NOT EXISTS "django_content_type"
(
    "id"        integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
    "app_label" varchar(100) NOT NULL,
    "model"     varchar(100) NOT NULL
);
CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");
CREATE TABLE IF NOT EXISTS "auth_group_permissions"
(
    "id"            integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "group_id"      integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id");
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");
CREATE TABLE IF NOT EXISTS "auth_permission"
(
    "id"              integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
    "content_type_id" integer      NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "codename"        varchar(100) NOT NULL,
    "name"            varchar(255) NOT NULL
);
CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");
CREATE TABLE IF NOT EXISTS "auth_group"
(
    "id"   integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(150) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "Tracker_parttype"
(
    "id"        integer     NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name"      varchar(50) NOT NULL,
    "num_steps" integer     NOT NULL
);
CREATE TABLE IF NOT EXISTS "Tracker_user_groups"
(
    "id"       integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id"  bigint  NOT NULL REFERENCES "Tracker_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "Tracker_user_user_permissions"
(
    "id"            integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id"       bigint  NOT NULL REFERENCES "Tracker_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "Tracker_partdoc"
(
    "id"           integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
    "is_image"     bool         NOT NULL,
    "part_step"    integer      NOT NULL,
    "file_name"    varchar(50)  NOT NULL,
    "file"         varchar(100) NOT NULL,
    "part_type_id" bigint       NULL REFERENCES "Tracker_parttype" ("id") DEFERRABLE INITIALLY DEFERRED,
    "uploader_id"  bigint       NULL REFERENCES "Tracker_user" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE UNIQUE INDEX "Tracker_user_groups_user_id_group_id_25429b3a_uniq" ON "Tracker_user_groups" ("user_id", "group_id");
CREATE INDEX "Tracker_user_groups_user_id_9ec32d2c" ON "Tracker_user_groups" ("user_id");
CREATE INDEX "Tracker_user_groups_group_id_7c19aff0" ON "Tracker_user_groups" ("group_id");
CREATE UNIQUE INDEX "Tracker_user_user_permissions_user_id_permission_id_bd63eaa1_uniq" ON "Tracker_user_user_permissions" ("user_id", "permission_id");
CREATE INDEX "Tracker_user_user_permissions_user_id_b52be2ad" ON "Tracker_user_user_permissions" ("user_id");
CREATE INDEX "Tracker_user_user_permissions_permission_id_18586754" ON "Tracker_user_user_permissions" ("permission_id");
CREATE INDEX "Tracker_partdoc_part_type_id_b58a3353" ON "Tracker_partdoc" ("part_type_id");
CREATE INDEX "Tracker_partdoc_uploader_id_b7602f2d" ON "Tracker_partdoc" ("uploader_id");
CREATE TABLE IF NOT EXISTS "django_admin_log"
(
    "id"              integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
    "object_id"       text         NULL,
    "object_repr"     varchar(200) NOT NULL,
    "action_flag"     smallint u
                          nsigned  NOT NULL CHECK ("action_flag" >= 0),
    "change_message"  text         NOT NULL,
    "content_type_id" integer      NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id"         bigint       NOT NULL REFERENCES "Tracker_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "action_time"     datetime     NOT NULL
);
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");
CREATE TABLE IF NOT EXISTS "django_session"
(
    "session_key"  varchar(40) NOT NULL PRIMARY KEY,
    "session_data" text        NOT NULL,
    "expire_date"  datetime    NOT NULL
);
CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");
CREATE TABLE IF NOT EXISTS "Tracker_orderitem"
(
    "id"       integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "order_id" bigint  NOT NULL REFERENCES "Tracker_order" ("id") DEFERRABLE INITIALLY DEFERRED,
    "part_id"  bigint  NOT NULL REFERENCES "Tracker_part" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX "Tracker_orderitem_order_id_e7727963" ON "Tracker_orderitem" ("order_id");
CREATE INDEX "Tracker_orderitem_part_id_826c13d7" ON "Tracker_orderitem" ("part_id");
CREATE TABLE IF NOT EXISTS "Tracker_step"
(
    "id"              integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "description"     text    NOT NULL,
    "part_model_id"   bigint  NOT NULL REFERENCES "Tracker_parttype" ("id") DEFERRABLE INITIALLY DEFERRED,
    "completion_time" time    NOT NULL,
    "step"            integer NOT NULL
);
CREATE INDEX "Tracker_step_part_model_id_3a72b490" ON "Tracker_step" ("part_model_id");
CREATE TABLE IF NOT EXISTS "Tracker_user"
(
    "id"           integer      NOT NULL PRIMARY KEY AUTOINCREMENT,
    "password"     varchar(128) NOT NULL,
    "last_login"   datetime     NULL,
    "is_superuser" bool         NOT NULL,
    "username"     varchar(150) NOT NULL UNIQUE,
    "first_name"   varchar(150) NOT NULL,
    "last_name"    varchar(150) NOT NULL,
    "email"        varchar(254) NOT NULL,
    "is_staff"     bool         NOT NULL,
    "is_active"    bool         NOT NULL,
    "date_joined"  datetime     NOT NULL,
    "company"      varchar(150) NOT NULL
);
CREATE TABLE IF NOT EXISTS "Tracker_order"
(
    "id"                   integer     NOT NULL PRIMARY KEY AUTOINCREMENT,
    "customer_id"          bigint      NULL REFERENCES "Tracker_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "estimated_completion" date        NULL,
    "name"                 varchar(50) NOT NULL,
    "status"               varchar(50) NOT NULL
);
CREATE INDEX "Tracker_order_customer_id_923a471e" ON "Tracker_order" ("customer_id");
CREATE TABLE IF NOT EXISTS "Tracker_part"
(
    "id"                   integer     NOT NULL PRIMARY KEY AUTOINCREMENT,
    "order_id"             bigint      NOT NULL REFERENCES "Tracker_order" ("id") DEFERRABLE INITIALLY DEFERRED,
    "part_type_id"         bigint      NULL REFERENCES "Tracker_parttype" ("id") DEFERRABLE INITIALLY DEFERRED,
    "step_id"              bigint      NULL REFERENCES "Tracker_step" ("id") DEFERRABLE INITIALLY DEFERRED,
    "assigned_emp_id"      bigint      NULL REFERENCES "Tracker_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "customer_id"          bigint      NULL REFERENCES "Tracker_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "estimated_completion" date        NULL,
    "name"                 varchar(50) NOT NULL,
    "status"               varchar(50) NOT NULL
);
CREATE INDEX "Tracker_part_order_id_9875b341" ON "Tracker_part" ("order_id");
CREATE INDEX "Tracker_part_part_type_id_9c53c9a0" ON "Tracker_part" ("part_type_id");
CREATE INDEX "Tracker_part_step_id_663a41e0" ON "Tracker_part" ("step_id");
CREATE INDEX "Tracker_part_assigned_emp_id_be9f51ad" ON "Tracker_part" ("assigned_emp_id");
CREATE INDEX "Tracker_part_customer_id_16120a15" ON "Tracker_part" ("customer_id");
