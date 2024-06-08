import os
from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID

from fastapi import Depends
from loguru import logger
from sqlmodel import Session, select

from dfapp.services.auth import utils as auth_utils
from dfapp.services.base import Service
from dfapp.services.database.models.variable.model import Variable, VariableCreate
from dfapp.services.deps import get_session

if TYPE_CHECKING:
    from dfapp.services.settings.service import SettingsService


class VariableService(Service):
    name = "variable_service"

    def __init__(self, settings_service: "SettingsService"):
        self.settings_service = settings_service

    def initialize_user_variables(self, user_id: Union[UUID, str], session: Session = Depends(get_session)):
        # Check for environment variables that should be stored in the database
        should_or_should_not = "Should" if self.settings_service.settings.store_environment_variables else "Should not"
        logger.info(f"{should_or_should_not} store environment variables in the database.")
        if self.settings_service.settings.store_environment_variables:
            for var in self.settings_service.settings.variables_to_get_from_environment:
                if var in os.environ:
                    logger.debug(f"Creating {var} variable from environment.")
                    if not session.exec(
                        select(Variable).where(Variable.user_id == user_id, Variable.name == var)
                    ).first():
                        try:
                            value = os.environ[var]
                            if isinstance(value, str):
                                value = value.strip()
                            self.create_variable(
                                user_id=user_id,
                                name=var,
                                value=value,
                                default_fields=[],
                                _type="Credential",
                                session=session,
                            )
                        except Exception as e:
                            logger.error(f"Error creating {var} variable: {e}")

        else:
            logger.info("Skipping environment variable storage.")

    def get_variable(
        self,
        user_id: Union[UUID, str],
        name: str,
        session: Session = Depends(get_session),
    ) -> str:
        # we get the credential from the database
        # credential = session.query(Variable).filter(Variable.user_id == user_id, Variable.name == name).first()
        variable = session.exec(select(Variable).where(Variable.user_id == user_id, Variable.name == name)).first()
        # we decrypt the value
        if not variable or not variable.value:
            raise ValueError(f"{name} variable not found.")
        decrypted = auth_utils.decrypt_api_key(variable.value, settings_service=self.settings_service)
        return decrypted

    def list_variables(self, user_id: Union[UUID, str], session: Session = Depends(get_session)) -> list[Optional[str]]:
        variables = session.exec(select(Variable).where(Variable.user_id == user_id)).all()
        return [variable.name for variable in variables]

    def update_variable(
        self,
        user_id: Union[UUID, str],
        name: str,
        value: str,
        session: Session = Depends(get_session),
    ):
        variable = session.exec(select(Variable).where(Variable.user_id == user_id, Variable.name == name)).first()
        if not variable:
            raise ValueError(f"{name} variable not found.")
        encrypted = auth_utils.encrypt_api_key(value, settings_service=self.settings_service)
        variable.value = encrypted
        session.add(variable)
        session.commit()
        session.refresh(variable)
        return variable

    def delete_variable(
        self,
        user_id: Union[UUID, str],
        name: str,
        session: Session = Depends(get_session),
    ):
        variable = session.exec(select(Variable).where(Variable.user_id == user_id, Variable.name == name)).first()
        if not variable:
            raise ValueError(f"{name} variable not found.")
        session.delete(variable)
        session.commit()
        return variable

    def create_variable(
        self,
        user_id: Union[UUID, str],
        name: str,
        value: str,
        default_fields: list[str] = [],
        _type: str = "Generic",
        session: Session = Depends(get_session),
    ):
        variable_base = VariableCreate(
            name=name,
            type=_type,
            value=auth_utils.encrypt_api_key(value, settings_service=self.settings_service),
            default_fields=default_fields,
        )
        variable = Variable.model_validate(variable_base, from_attributes=True, update={"user_id": user_id})
        session.add(variable)
        session.commit()
        session.refresh(variable)
        return variable
