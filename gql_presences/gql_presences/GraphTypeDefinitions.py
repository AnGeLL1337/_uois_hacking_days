from typing import List, Union
import typing
from unittest import result
import strawberry as strawberryA
import uuid
import datetime
from contextlib import asynccontextmanager

@asynccontextmanager
async def withInfo(info):
    asyncSessionMaker = info.context['asyncSessionMaker']
    async with asyncSessionMaker() as session:
        try:
            yield session
        finally:
            pass


def AsyncSessionFromInfo(info):
    print('obsolete function used AsyncSessionFromInfo, use withInfo context manager instead')
    return info.context['session']

###########################################################################################################################
#
# zde definujte sve GQL modely
# - nove, kde mate zodpovednost
# - rozsirene, ktere existuji nekde jinde a vy jim pridavate dalsi atributy
#
###########################################################################################################################
#
# priklad rozsireni UserGQLModel
#
from gql_presences.GraphResolvers import resolvePresenceModelPage, resolvePresenceModelById
from gql_presences.GraphResolvers import resolvePresenceTypeModelPage,resolvePresenceTypeModelById, resolvePresencesForPresenceType
from gql_presences.GraphResolvers import resolvePresencesForUser
from gql_presences.GraphResolvers import resolveTaskModelByPage, resolveTaskModelById, resolveTasksForUser
from gql_presences.GraphResolvers import resolveContentModelByPage, resolveContentModelById, resolveContentForEvent
from gql_presences.GraphResolvers import resolvePresencesOnEvent


@strawberryA.federation.type(keys=["id"], description="""Entity representing presence""")
class PresenceGQLModel:

    @classmethod
    async def resolve_reference(cls, info: strawberryA.types.Info, id: strawberryA.ID):
        async with withInfo(info) as session:
            result = await resolvePresenceModelById(session, id)
            result._type_definition = cls._type_definition # little hack :)
            return result

    @strawberryA.field(description="""primary key""")
    def id(self) -> strawberryA.ID:
        return self.id
    
    @strawberryA.field(description="""PresenceTypeId""")
    async def presence_type(self, info: strawberryA.types.Info) -> 'PresenceTypeGQLModel':
        async with withInfo(info) as session:
            result = await resolvePresenceTypeModelById(session, self.presenceType_id)
            return result

    @strawberryA.field(description="""user id""")
    async def user(self, info: strawberryA.types.Info) -> 'UserGQLModel':
        result = UserGQLModel(id=self.user_id)
        return result
    
    @strawberryA.field(description="""event id""")
    async def event(self, info: strawberryA.types.Info) -> 'EventGQLModel':
        result = EventGQLModel(id=self.event)
        return result

   
   
@strawberryA.federation.type(keys=["id"], description="""Entity representing presence type""")
class PresenceTypeGQLModel:
    @classmethod
    async def resolve_reference(cls, info: strawberryA.types.Info, id: strawberryA.ID):
        async with withInfo(info) as session:
            result = await resolvePresenceTypeModelById(session, id)
            result._type_definition = cls._type_definition # little hack :)
            return result

    @strawberryA.field(description="""primary key""")
    def id(self) -> strawberryA.ID:
        return self.id

    @strawberryA.field(description="""Presence type name (absent/present)""")
    def name(self) -> str:
        return self.name

    @strawberryA.field(description="""PresenceId""")
    #výstupem bude list
    async def presences(self, info: strawberryA.types.Info) -> typing.List['PresenceGQLModel']:
        async with withInfo(info) as session:
            result = await resolvePresencesForPresenceType(session, self.id)
            return result

@strawberryA.federation.type(keys=["id"], description="""Entity representing tasks""")
class TaskGQLModel:
    @classmethod
    async def resolve_reference(cls, info: strawberryA.types.Info, id:strawberryA.ID):
        async with withInfo(info) as session:
            result = await resolveTaskModelById(session, id)
            result._type_definition = cls._type_definition
            return result
    
    @strawberryA.field(description="""Primary key of task""")
    def id(self) -> strawberryA.ID:
        return self.id
    
    @strawberryA.field(description="""Name of tasks""")
    def name(self) -> str:
        return self.name
    
    @strawberryA.field(description="""Brief description""")
    def brief_desc(self) -> str:
        return self.brief_desc
    
    @strawberryA.field(description="""Full description""")
    def detailed_desc(self) -> str:
        return self.detailed_desc
    
    @strawberryA.field(description=""" Reference""")
    def reference(self) -> str:
        return self.reference
    
    @strawberryA.field(description="""Date of entry""")
    def date_of_entry(self) -> datetime.date:
        return self.date_of_entry
    
    @strawberryA.field(description="""Date of submission""")
    def date_of_submission(self) -> datetime.date:
        return self.date_of_submission
    
    @strawberryA.field(description="""Date of fullfilment""")
    def date_of_fulfillment(self) -> datetime.date:
        return self.date_of_fulfillment

    @strawberryA.field(description="""event id""")
    async def event(self, info: strawberryA.types.Info) -> 'EventGQLModel':
        result = EventGQLModel(id=self.event_id)
        return result


@strawberryA.federation.type(keys=["id"], description="""Entity representing content""")
class ContentGQLModel:
    @classmethod
    async def resolve_reference(cls, info: strawberryA.types.Info, id:strawberryA.ID):
        async with withInfo(info) as session:
            result = await resolveContentModelById(session, id)
            result._type_definition = cls._type_definition
            return result

    @strawberryA.field(description="""Primary key of content""")
    def id(self) -> strawberryA.ID:
        return self.id 

    @strawberryA.field(description="""Brief description""")
    def brief_desc(self) -> str:
        return self.brief_desc
    
    @strawberryA.field(description="""Full description""")
    def detailed_desc(self) -> str:
        return self.detailed_desc

    @strawberryA.field(description="""event id""")
    async def event(self, info: strawberryA.types.Info) -> 'EventGQLModel':
        result = EventGQLModel(id=self.event_id)
        return result
    
    # DODĚLAT BRIEF A FULL DESC

   
    
@strawberryA.federation.type(extend=True, keys=["id"])
class UserGQLModel:
    
    id: strawberryA.ID = strawberryA.federation.field(external=True)

    
    @classmethod
    def resolve_reference(cls, id: strawberryA.ID):
        return UserGQLModel(id=id) # jestlize rozsirujete, musi byt tento vyraz
    
    @strawberryA.field(description="""presence id""")
    async def presences(self, info: strawberryA.types.Info) -> typing.List['PresenceGQLModel']:
        async with withInfo(info) as session:
            result = await resolvePresencesForUser(session, self.id)
            return result

    @strawberryA.field(description="""task id""")
    async def tasks(self, info: strawberryA.types.Info) -> typing.List['TaskGQLModel']:
        async with withInfo(info) as session:
            result = await resolveTasksForUser(session, self.id)
            return result
    

@strawberryA.federation.type(extend=True, keys=["id"])
class EventGQLModel:
    id: strawberryA.ID = strawberryA.federation.field(external=True)

    @classmethod
    def resolve_reference(cls, id: strawberryA.ID):
        return EventGQLModel(id=id) # jestlize rozsirujete, musi byt tento vyraz

    # relace (1,N)
    @strawberryA.field(description="""presence id""")
    async def presences(self, info: strawberryA.types.Info) -> typing.List['PresenceGQLModel']:
        async with withInfo(info) as session:
            result = await resolvePresencesOnEvent(session, self.id)
            return result
    
    # rozšiřujeme jen o atributy (1,1)
    @strawberryA.field(description="""content id""")
    async def content(self, info: strawberryA.types.Info) -> typing.Union['ContentGQLModel', None]: 
        async with withInfo(info) as session:
            result = await resolveContentForEvent(session, self.id) # z tabulky obsahů hledáme event_id = event_id v Content
            return next (result,None)
     
#     zde je rozsireni o dalsi resolvery¨
#     async def external_ids(self, info: strawberryA.types.Info) -> List['ExternalIdGQLModel']:
#         result = await resolveExternalIds(session,  self.id)
#         return result


###########################################################################################################################
#
# zde definujte svuj Query model
#
###########################################################################################################################

@strawberryA.type(description="""Type for query root""")
class Query:
   # nedotazovat se na TaskOnEventModel
    @strawberryA.field(description="""Finds a workflow by their id""")
    async def say_hello(self, info: strawberryA.types.Info, id: uuid.UUID) -> Union[str, None]:
        result = f'Hello {id}'
        return result

    @strawberryA.field(description="""Finds presence by their id""")
    async def presence_by_id(self, info: strawberryA.types.Info, id: uuid.UUID) -> Union[PresenceGQLModel, None]:
        async with withInfo(info) as session:
            result = await resolvePresenceModelById(session, id)
            return result
    
    @strawberryA.field(description="""Finds presence by their page""")
    async def presence_page(self, info: strawberryA.types.Info, skip: int = 0, limit: int = 10) -> List[PresenceGQLModel]:
        async with withInfo(info) as session:
            result = await resolvePresenceModelPage(session, skip, limit)
            return result

    @strawberryA.field(description="""Finds presence type by their id""")
    async def presence_type_by_id(self, info: strawberryA.types.Info, id: uuid.UUID) -> Union[PresenceTypeGQLModel, None]:
        async with withInfo(info) as session:
            result = await resolvePresenceTypeModelById(session, id)
            return result
    
    @strawberryA.field(description="""Finds presence by their page""")
    async def presence_type_page(self, info: strawberryA.types.Info, skip: int = 0, limit: int = 10) -> List[PresenceTypeGQLModel]:
        async with withInfo(info) as session:
            result = await resolvePresenceTypeModelPage(session, skip, limit)
            return result
    
    @strawberryA.field(description="""Finds tasks by their id""")
    async def task_by_id(self, info: strawberryA.types.Info, id: uuid.UUID) -> Union[TaskGQLModel, None]:
        async with withInfo(info) as session:
            result = await resolveTaskModelById(session, id)
            return result
    
    @strawberryA.field(description="""Finds tasks by their page""")
    async def task_page(self, info: strawberryA.types.Info, id: uuid.UUID) -> List[TaskGQLModel]:
        async with withInfo(info) as session:
            result = await resolveTaskModelByPage(session, id)
            return result

    @strawberryA.field(description="""Finds content by their id""")
    async def content_by_id(self, info: strawberryA.types.Info, id: uuid.UUID) -> Union[ContentGQLModel, None]:
        async with withInfo(info) as session:
            result = await resolveContentModelById(session, id)
            return result
    
    @strawberryA.field(description="""Finds content by their page""")
    async def content_page(self, info: strawberryA.types.Info, id: uuid.UUID) -> List[ContentGQLModel]:
        async with withInfo(info) as session:
            result = await resolveContentModelByPage(session, id)
            return result

    #264 - 267
    # volat funkci 
    # 
    
    #radnomPresenceData 
    #async def ....
    #zavolat funkci 
    #předat výstup výsledku dotazu
    #vrátit hlavní datovou strukturu
    #resolvePresenceModelById
  

    
###########################################################################################################################
#
# Schema je pouzito v main.py, vsimnete si parametru types, obsahuje vyjmenovane modely. Bez explicitniho vyjmenovani
# se ve schema objevi jen ty struktury, ktere si strawberry dokaze odvodit z Query. Protoze v teto konkretni implementaci
# nektere modely nejsou s Query propojene je potreba je explicitne vyjmenovat. Jinak ve federativnim schematu nebude
# dostupne rozsireni, ktere tento prvek federace implementuje.
#
###########################################################################################################################

schema = strawberryA.federation.Schema(Query, types=(UserGQLModel, EventGQLModel))