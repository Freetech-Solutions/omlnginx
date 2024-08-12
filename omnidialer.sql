--
-- PostgreSQL database dump
--

-- Dumped from database version 14.9 (Debian 14.9-1.pgdg110+1)
-- Dumped by pg_dump version 14.9 (Debian 14.9-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: campaign; Type: TABLE; Schema: public; Owner: omnidialer
--

CREATE TABLE public.campaign (
    id integer NOT NULL,
    estado integer NOT NULL,
    call_strategy integer[] NOT NULL,
    nombre character varying(128) NOT NULL,
    fecha_inicio date,
    fecha_fin date,
    oculto boolean NOT NULL,
    campaign_id_wombat integer,
    type integer NOT NULL,
    tipo_interaccion integer NOT NULL,
    es_template boolean NOT NULL,
    nombre_template character varying(128),
    es_manual boolean NOT NULL,
    objetivo integer NOT NULL,
    tiempo_desconexion integer NOT NULL,
    bd_contacto_id integer,
    reported_by_id integer NOT NULL,
    sitio_externo_id integer,
    mostrar_nombre boolean NOT NULL,
    id_externo character varying(128),
    sistema_externo_id integer,
    campo_desactivacion character varying(128),
    campos_bd_no_editables character varying(2052) NOT NULL,
    campos_bd_ocultos character varying(2052) NOT NULL,
    outcid character varying(128),
    outr_id integer,
    videocall_habilitada boolean NOT NULL,
    speech text,
    campo_direccion character varying(128),
    mostrar_did boolean NOT NULL,
    mostrar_nombre_ruta_entrante boolean NOT NULL,
    control_de_duplicados integer NOT NULL,
    prioridad integer NOT NULL,
    campos_bd_obligatorios character varying(2052) NOT NULL,
    whatsapp_habilitado boolean NOT NULL,
    sunday boolean NOT NULL,
    monday boolean NOT NULL,
    tuesday boolean NOT NULL,
    wednesday boolean NOT NULL,
    thursday boolean NOT NULL,
    friday boolean NOT NULL,
    saturday boolean NOT NULL,
    hour_start time without time zone NOT NULL,
    hour_ends time without time zone NOT NULL,
    timeout bigint,
    retry bigint,
    maxlen bigint NOT NULL,
    wrapuptime bigint NOT NULL,
    servicelevel bigint NOT NULL,
    strategy character varying(128) NOT NULL,
    eventmemberstatus boolean NOT NULL,
    eventwhencalled boolean NOT NULL,
    weight bigint NOT NULL,
    ringinuse boolean NOT NULL,
    setinterfacevar boolean NOT NULL,
    wait integer NOT NULL,
    auto_grabacion boolean NOT NULL,
    detectar_contestadores boolean NOT NULL,
    ep_id_wombat integer,
    announce character varying(128),
    announce_frequency bigint,
    initial_predictive_model boolean NOT NULL,
    initial_boost_factor numeric(3,1),
    musiconhold_id integer,
    context character varying(128),
    monitor_join boolean,
    monitor_format character varying(128),
    queue_youarenext character varying(128),
    queue_thereare character varying(128),
    queue_callswaiting character varying(128),
    queue_holdtime character varying(128),
    queue_minutes character varying(128),
    queue_seconds character varying(128),
    queue_lessthan character varying(128),
    queue_thankyou character varying(128),
    queue_reporthold character varying(128),
    announce_round_seconds bigint,
    announce_holdtime character varying(128) NOT NULL,
    joinempty character varying(128),
    leavewhenempty character varying(128),
    reportholdtime boolean,
    memberdelay bigint,
    timeoutrestart boolean,
    audio_de_ingreso_id integer,
    audio_para_contestadores_id integer,
    audios_id integer,
    dial_timeout integer,
    destino_id integer,
    ivr_breakdown_id integer,
    announce_position boolean NOT NULL,
    wait_announce_frequency bigint,
    audio_previo_conexion_llamada_id integer,
    CONSTRAINT campaign_control_de_duplicados_check CHECK ((control_de_duplicados >= 0)),
    CONSTRAINT campaign_dial_timeout_check CHECK ((dial_timeout >= 0)),
    CONSTRAINT campaign_estado_check CHECK ((estado >= 0)),
    CONSTRAINT campaign_objetivo_check CHECK ((objetivo >= 0)),
    CONSTRAINT campaign_prioridad_check CHECK ((prioridad >= 0)),
    CONSTRAINT campaign_tiempo_desconexion_check CHECK ((tiempo_desconexion >= 0)),
    CONSTRAINT campaign_tipo_interaccion_check CHECK ((tipo_interaccion >= 0)),
    CONSTRAINT campaign_type_check CHECK ((type >= 0)),
    CONSTRAINT campaign_wait_check CHECK ((wait >= 0))
);


ALTER TABLE public.campaign OWNER TO omnidialer;

--
-- Name: campaign_historic; Type: TABLE; Schema: public; Owner: omnidialer
--

CREATE TABLE public.campaign_historic (
)
INHERITS (public.campaign);


ALTER TABLE public.campaign_historic OWNER TO omnidialer;

--
-- Name: campaign_id_seq; Type: SEQUENCE; Schema: public; Owner: omnidialer
--

CREATE SEQUENCE public.campaign_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.campaign_id_seq OWNER TO omnidialer;

--
-- Name: campaign_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnidialer
--

ALTER SEQUENCE public.campaign_id_seq OWNED BY public.campaign.id;


--
-- Name: contact; Type: TABLE; Schema: public; Owner: omnidialer
--

CREATE TABLE public.contact (
    id integer NOT NULL,
    telefono character varying(128) NOT NULL,
    datos text NOT NULL,
    bd_contacto_id integer,
    es_originario boolean NOT NULL,
    id_externo character varying(128)
);


ALTER TABLE public.contact OWNER TO omnidialer;

--
-- Name: contact_id_seq; Type: SEQUENCE; Schema: public; Owner: omnidialer
--

CREATE SEQUENCE public.contact_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contact_id_seq OWNER TO omnidialer;

--
-- Name: contact_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnidialer
--

ALTER SEQUENCE public.contact_id_seq OWNED BY public.contact.id;


--
-- Name: contact_in_campaign; Type: TABLE; Schema: public; Owner: omnidialer
--

CREATE TABLE public.contact_in_campaign (
    id_campaign integer NOT NULL,
    id_contact integer NOT NULL,
    id integer NOT NULL,
    status integer NOT NULL
);


ALTER TABLE public.contact_in_campaign OWNER TO omnidialer;

--
-- Name: COLUMN contact_in_campaign.id_campaign; Type: COMMENT; Schema: public; Owner: omnidialer
--

COMMENT ON COLUMN public.contact_in_campaign.id_campaign IS 'foreign key to campaign table';


--
-- Name: COLUMN contact_in_campaign.id_contact; Type: COMMENT; Schema: public; Owner: omnidialer
--

COMMENT ON COLUMN public.contact_in_campaign.id_contact IS 'link to contact table';


--
-- Name: contact_in_campaign_historic; Type: TABLE; Schema: public; Owner: omnidialer
--

CREATE TABLE public.contact_in_campaign_historic (
)
INHERITS (public.contact_in_campaign);


ALTER TABLE public.contact_in_campaign_historic OWNER TO omnidialer;

--
-- Name: incidence_rules; Type: TABLE; Schema: public; Owner: omnidialer
--

CREATE TABLE public.incidence_rules (
    id integer NOT NULL,
    estado integer NOT NULL,
    estado_personalizado character varying(128),
    intento_max integer NOT NULL,
    reintentar_tarde integer NOT NULL,
    en_modo integer NOT NULL,
    campaign_id integer NOT NULL,
    CONSTRAINT incidence_rules_en_modo_check CHECK ((en_modo >= 0)),
    CONSTRAINT incidence_rules_estado_check CHECK ((estado >= 0))
);


ALTER TABLE public.incidence_rules OWNER TO omnidialer;

--
-- Name: incidence_rules_historic; Type: TABLE; Schema: public; Owner: omnidialer
--

CREATE TABLE public.incidence_rules_historic (
)
INHERITS (public.incidence_rules);


ALTER TABLE public.incidence_rules_historic OWNER TO omnidialer;

--
-- Name: incidence_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: omnidialer
--

CREATE SEQUENCE public.incidence_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.incidence_rules_id_seq OWNER TO omnidialer;

--
-- Name: incidence_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: omnidialer
--

ALTER SEQUENCE public.incidence_rules_id_seq OWNED BY public.incidence_rules.id;


--
-- Name: campaign id; Type: DEFAULT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.campaign ALTER COLUMN id SET DEFAULT nextval('public.campaign_id_seq'::regclass);


--
-- Name: campaign_historic id; Type: DEFAULT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.campaign_historic ALTER COLUMN id SET DEFAULT nextval('public.campaign_id_seq'::regclass);


--
-- Name: contact id; Type: DEFAULT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.contact ALTER COLUMN id SET DEFAULT nextval('public.contact_id_seq'::regclass);


--
-- Name: incidence_rules id; Type: DEFAULT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.incidence_rules ALTER COLUMN id SET DEFAULT nextval('public.incidence_rules_id_seq'::regclass);


--
-- Name: incidence_rules_historic id; Type: DEFAULT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.incidence_rules_historic ALTER COLUMN id SET DEFAULT nextval('public.incidence_rules_id_seq'::regclass);


--
-- Name: campaign_historic campaign_historic_pkey; Type: CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.campaign_historic
    ADD CONSTRAINT campaign_historic_pkey PRIMARY KEY (id);


--
-- Name: campaign campaign_nombre_key; Type: CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.campaign
    ADD CONSTRAINT campaign_nombre_key UNIQUE (nombre);


--
-- Name: campaign campaign_pkey; Type: CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.campaign
    ADD CONSTRAINT campaign_pkey PRIMARY KEY (id);


--
-- Name: contact_in_campaign_historic contact_in_campaign_historic_pkey; Type: CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.contact_in_campaign_historic
    ADD CONSTRAINT contact_in_campaign_historic_pkey PRIMARY KEY (id);


--
-- Name: contact contact_pkey; Type: CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.contact
    ADD CONSTRAINT contact_pkey PRIMARY KEY (id);


--
-- Name: incidence_rules incidence_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.incidence_rules
    ADD CONSTRAINT incidence_rules_pkey PRIMARY KEY (id);


--
-- Name: contact_in_campaign primary_key_contact_in_campaign; Type: CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.contact_in_campaign
    ADD CONSTRAINT primary_key_contact_in_campaign PRIMARY KEY (id);


--
-- Name: campaign_bd_contacto_id_3b5858cd; Type: INDEX; Schema: public; Owner: omnidialer
--

CREATE INDEX campaign_bd_contacto_id_3b5858cd ON public.campaign USING btree (bd_contacto_id);


--
-- Name: campaign_nombre_da9ee190_like; Type: INDEX; Schema: public; Owner: omnidialer
--

CREATE INDEX campaign_nombre_da9ee190_like ON public.campaign USING btree (nombre varchar_pattern_ops);


--
-- Name: campaign_outr_id_2cd2dd43; Type: INDEX; Schema: public; Owner: omnidialer
--

CREATE INDEX campaign_outr_id_2cd2dd43 ON public.campaign USING btree (outr_id);


--
-- Name: campaign_reported_by_id_cb70293d; Type: INDEX; Schema: public; Owner: omnidialer
--

CREATE INDEX campaign_reported_by_id_cb70293d ON public.campaign USING btree (reported_by_id);


--
-- Name: contact_bd_contacto_id_e36d02df; Type: INDEX; Schema: public; Owner: omnidialer
--

CREATE INDEX contact_bd_contacto_id_e36d02df ON public.contact USING btree (bd_contacto_id);


--
-- Name: fki_contact_in_campaign_fkey_contact; Type: INDEX; Schema: public; Owner: omnidialer
--

CREATE INDEX fki_contact_in_campaign_fkey_contact ON public.contact_in_campaign_historic USING btree (id_contact);


--
-- Name: fki_contact_in_campaign_historic_fkey_campaign; Type: INDEX; Schema: public; Owner: omnidialer
--

CREATE INDEX fki_contact_in_campaign_historic_fkey_campaign ON public.contact_in_campaign_historic USING btree (id_campaign);


--
-- Name: fki_foreign_key_contact; Type: INDEX; Schema: public; Owner: omnidialer
--

CREATE INDEX fki_foreign_key_contact ON public.contact_in_campaign USING btree (id_contact);


--
-- Name: fki_incidence_rules_historic_fkey_campaign_id; Type: INDEX; Schema: public; Owner: omnidialer
--

CREATE INDEX fki_incidence_rules_historic_fkey_campaign_id ON public.incidence_rules_historic USING btree (campaign_id);


--
-- Name: incidence_rules_campaign_id_707899e9; Type: INDEX; Schema: public; Owner: omnidialer
--

CREATE INDEX incidence_rules_campaign_id_707899e9 ON public.incidence_rules USING btree (campaign_id);


--
-- Name: contact_in_campaign_historic contact_in_campaign_fkey_contact; Type: FK CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.contact_in_campaign_historic
    ADD CONSTRAINT contact_in_campaign_fkey_contact FOREIGN KEY (id_contact) REFERENCES public.contact(id) NOT VALID;


--
-- Name: contact_in_campaign_historic contact_in_campaign_historic_fkey_campaign; Type: FK CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.contact_in_campaign_historic
    ADD CONSTRAINT contact_in_campaign_historic_fkey_campaign FOREIGN KEY (id_campaign) REFERENCES public.campaign_historic(id) NOT VALID;


--
-- Name: contact_in_campaign foreign_key_campaign; Type: FK CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.contact_in_campaign
    ADD CONSTRAINT foreign_key_campaign FOREIGN KEY (id_campaign) REFERENCES public.campaign(id) NOT VALID;


--
-- Name: contact_in_campaign foreign_key_contact; Type: FK CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.contact_in_campaign
    ADD CONSTRAINT foreign_key_contact FOREIGN KEY (id_contact) REFERENCES public.contact(id) NOT VALID;


--
-- Name: incidence_rules_historic incidence_rules_historic_fkey_campaign_id; Type: FK CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.incidence_rules_historic
    ADD CONSTRAINT incidence_rules_historic_fkey_campaign_id FOREIGN KEY (campaign_id) REFERENCES public.campaign_historic(id) NOT VALID;


--
-- Name: incidence_rules re_campaign_id_707899e9_fk_ominicont; Type: FK CONSTRAINT; Schema: public; Owner: omnidialer
--

ALTER TABLE ONLY public.incidence_rules
    ADD CONSTRAINT re_campaign_id_707899e9_fk_ominicont FOREIGN KEY (campaign_id) REFERENCES public.campaign(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--
