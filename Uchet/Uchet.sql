-- Table: bpd.class

-- DROP TABLE IF EXISTS bpd.class;

CREATE TABLE IF NOT EXISTS bpd.class
(
    id bigint NOT NULL DEFAULT nextval('bpd.class_id_seq'::regclass),
    id_con bigint NOT NULL,
    id_group bigint NOT NULL,
    id_parent bigint NOT NULL,
    id_root bigint NOT NULL,
    level integer NOT NULL,
    name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    "desc" character varying(2044) COLLATE pg_catalog."default" NOT NULL DEFAULT 'н/д'::text,
    "on" boolean NOT NULL,
    on_extensible boolean NOT NULL DEFAULT true,
    on_abstraction boolean NOT NULL DEFAULT true,
    id_unit_conversion_rule integer NOT NULL,
    barcode_manufacturer bigint NOT NULL DEFAULT 0,
    barcode_local bigint NOT NULL DEFAULT 0,
    "timestamp" timestamp without time zone NOT NULL DEFAULT LOCALTIMESTAMP,
    on_freeze boolean NOT NULL DEFAULT false,
    id_group_root bigint NOT NULL DEFAULT 0,
    timestamp_parent timestamp without time zone NOT NULL DEFAULT LOCALTIMESTAMP(3),
    id_unit integer NOT NULL DEFAULT '-1'::integer,
    timestamp_root timestamp without time zone NOT NULL,
    timestamp_child_change timestamp without time zone NOT NULL DEFAULT LOCALTIMESTAMP(3),
    name_format character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'none'::character varying,
    quantity_show boolean NOT NULL DEFAULT true,
    path_array bigint[] NOT NULL DEFAULT ARRAY[0],
    ready boolean NOT NULL,
    CONSTRAINT class_pkey PRIMARY KEY (id),
    CONSTRAINT lnk_class_group FOREIGN KEY (id_group)
        REFERENCES bpd."group" (id) MATCH FULL
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT lnk_conception_class FOREIGN KEY (id_con)
        REFERENCES bpd.conception (id) MATCH FULL
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT id CHECK (id > 0),
    CONSTRAINT id_root CHECK (id >= 0)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS bpd.class
    OWNER to funcowner;

REVOKE ALL ON TABLE bpd.class FROM funcowner;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE ON TABLE bpd.class TO funcowner;
-- Index: index_class_conception

-- DROP INDEX IF EXISTS bpd.index_class_conception;

CREATE INDEX IF NOT EXISTS index_class_conception
    ON bpd.class USING btree
    (id_con ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: index_class_id

-- DROP INDEX IF EXISTS bpd.index_class_id;

CREATE INDEX IF NOT EXISTS index_class_id
    ON bpd.class USING btree
    (id ASC NULLS LAST, "timestamp" ASC NULLS LAST)
    TABLESPACE pg_default;

ALTER TABLE IF EXISTS bpd.class
    CLUSTER ON index_class_id;
-- Index: index_class_id_group

-- DROP INDEX IF EXISTS bpd.index_class_id_group;

CREATE INDEX IF NOT EXISTS index_class_id_group
    ON bpd.class USING btree
    (id_group ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: index_class_id_parent

-- DROP INDEX IF EXISTS bpd.index_class_id_parent;

CREATE INDEX IF NOT EXISTS index_class_id_parent
    ON bpd.class USING btree
    (id_parent ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: index_class_is_actual

-- DROP INDEX IF EXISTS bpd.index_class_is_actual;

CREATE INDEX IF NOT EXISTS index_class_is_actual
    ON bpd.class USING btree
    (id ASC NULLS LAST)
    INCLUDE("timestamp", timestamp_child_change)
    TABLESPACE pg_default;
-- Index: index_class_name

-- DROP INDEX IF EXISTS bpd.index_class_name;

CREATE INDEX IF NOT EXISTS index_class_name
    ON bpd.class USING btree
    (lower(name::text) COLLATE pg_catalog."ru-RU-x-icu" varchar_pattern_ops ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: index_class_path_array

-- DROP INDEX IF EXISTS bpd.index_class_path_array;

CREATE INDEX IF NOT EXISTS index_class_path_array
    ON bpd.class USING btree
    (path_array ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: index_class_root

-- DROP INDEX IF EXISTS bpd.index_class_root;

CREATE INDEX IF NOT EXISTS index_class_root
    ON bpd.class USING btree
    (id_root ASC NULLS LAST)
    TABLESPACE pg_default;

-- Trigger: trigger_class_after_del_link

-- DROP TRIGGER IF EXISTS trigger_class_after_del_link ON bpd.class;

CREATE TRIGGER trigger_class_after_del_link
    AFTER DELETE
    ON bpd.class
    FOR EACH ROW
    EXECUTE FUNCTION bpd.trg_entity_can_link_link_val_del();