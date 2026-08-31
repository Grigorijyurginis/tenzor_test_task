-- Индекс по parent_id: на нём строится как подъём от сотрудника к офису, так и спуск по всему поддереву офиса.
CREATE INDEX IF NOT EXISTS idx_org_units_parent_id ON org_units (parent_id);
