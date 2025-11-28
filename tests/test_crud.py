import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
import schemas
import crud
from database import Base


@pytest.fixture()
def session():
    
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- USUARIOS ---

def test_crear_y_obtener_usuarios_activos(session):
    # Arrange
    u1 = schemas.UsuarioCrear(nombre="Ana", telefono="111")
    u2 = schemas.UsuarioCrear(nombre="Ben", telefono="222")

    crud.crear_usuario(session, u1)
    crud.crear_usuario(session, u2)

    # Act
    usuarios = crud.obtener_usuarios(session)

    # Assert
    assert len(usuarios) == 2
    assert {u.nombre for u in usuarios} == {"Ana", "Ben"}


def test_eliminar_usuario_es_logico(session):
    u = crud.crear_usuario(session, schemas.UsuarioCrear(nombre="Carlos", telefono="333"))

    # eliminar (borrado lógico)
    eliminado = crud.eliminar_usuario(session, u.id)
    assert eliminado is not None
    assert eliminado.activo is False

    # obtener_usuarios no debe listar inactivos
    activos = crud.obtener_usuarios(session)
    assert all(x.activo for x in activos)
    assert all(x.id != u.id for x in activos)


def test_inactivar_usuario_id_inexistente(session):
    # No existe id 999
    res = crud.inactivar_usuario(session, 999)
    assert res is None


def test_obtener_usuarios_por_estado(session):
    u1 = crud.crear_usuario(session, schemas.UsuarioCrear(nombre="Act", telefono="1"))
    u2 = crud.crear_usuario(session, schemas.UsuarioCrear(nombre="Inact", telefono="2"))

    crud.inactivar_usuario(session, u2.id)

    activos = crud.obtener_usuarios_por_estado(session, True)
    inactivos = crud.obtener_usuarios_por_estado(session, False)

    assert {u.id for u in activos} == {u1.id}
    assert {u.id for u in inactivos} == {u2.id}


def test_buscar_usuario_por_nombre_ilike(session):
    crud.crear_usuario(session, schemas.UsuarioCrear(nombre="María Pérez", telefono="1"))
    crud.crear_usuario(session, schemas.UsuarioCrear(nombre="Mario", telefono="2"))
    crud.crear_usuario(session, schemas.UsuarioCrear(nombre="Ana", telefono="3"))

    encontrados = crud.buscar_usuario_por_nombre(session, "mar")
    assert {u.nombre for u in encontrados} == {"María Pérez", "Mario"}


# --- CONDUCTORES ---

def test_crear_y_listar_conductores_activos(session):
    crud.crear_conductor(session, schemas.ConductorCrear(nombre="C1", licencia="L1"))
    crud.crear_conductor(session, schemas.ConductorCrear(nombre="C2", licencia=None))

    conductores = crud.obtener_conductores(session)
    assert len(conductores) == 2
    assert all(c.activo for c in conductores)


def test_inactivar_conductor(session):
    c = crud.crear_conductor(session, schemas.ConductorCrear(nombre="Driver", licencia="ABC"))

    inact = crud.inactivar_conductor(session, c.id)
    assert inact is not None and inact.activo is False

    # no debe aparecer en los activos
    activos = crud.obtener_conductores(session)
    assert all(x.id != c.id for x in activos)


def test_conductores_por_estado(session):
    c1 = crud.crear_conductor(session, schemas.ConductorCrear(nombre="A", licencia="1"))
    c2 = crud.crear_conductor(session, schemas.ConductorCrear(nombre="B", licencia="2"))
    crud.inactivar_conductor(session, c2.id)

    activos = crud.obtener_conductores_por_estado(session, True)
    inactivos = crud.obtener_conductores_por_estado(session, False)

    assert {c.id for c in activos} == {c1.id}
    assert {c.id for c in inactivos} == {c2.id}


# --- VEHICULOS ---

def test_crear_y_listar_vehiculos_activos(session):
    crud.crear_vehiculo(session, schemas.VehiculoCrear(placa="XYZ123", modelo="M1"))
    crud.crear_vehiculo(session, schemas.VehiculoCrear(placa="ABC999", modelo=None))

    vehiculos = crud.obtener_vehiculos(session)
    assert len(vehiculos) == 2
    assert all(v.activo for v in vehiculos)


def test_inactivar_vehiculo_inexistente(session):
    res = crud.inactivar_vehiculo(session, 555)
    assert res is None


def test_buscar_vehiculo_por_placa_ilike(session):
    crud.crear_vehiculo(session, schemas.VehiculoCrear(placa="MTX-111", modelo="M1"))
    crud.crear_vehiculo(session, schemas.VehiculoCrear(placa="MTY-222", modelo="M2"))
    crud.crear_vehiculo(session, schemas.VehiculoCrear(placa="ZZZ-333", modelo="M3"))

    encontrados = crud.buscar_vehiculo_por_placa(session, "mt")
    assert {v.placa for v in encontrados} == {"MTX-111", "MTY-222"}


# --- VIAJES ---

def test_crear_y_listar_viajes_activos(session):
    # Datos relacionados mínimos
    u = crud.crear_usuario(session, schemas.UsuarioCrear(nombre="User", telefono="000"))
    c = crud.crear_conductor(session, schemas.ConductorCrear(nombre="Cond", licencia="L"))
    v = crud.crear_vehiculo(session, schemas.VehiculoCrear(placa="PLK-001", modelo="S"))

    crud.crear_viaje(session, schemas.ViajeCrear(usuario_id=u.id, conductor_id=c.id, vehiculo_id=v.id, destino="X"))

    viajes = crud.obtener_viajes(session)
    assert len(viajes) == 1
    assert viajes[0].usuario_id == u.id
    assert viajes[0].conductor_id == c.id
    assert viajes[0].vehiculo_id == v.id
    assert viajes[0].activo is True
