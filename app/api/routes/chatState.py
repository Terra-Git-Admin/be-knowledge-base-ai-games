from fastapi import APIRouter
from app.core.services.chatStateFlowServices import chatStateFlowServices
from app.core.schema.ChatStateSchema import ChatStateFlow
from typing import List, Dict


chatStateRouter = APIRouter(
    prefix="/files",
    tags=["Chat State Flows"]
)

@chatStateRouter.post("/chatState")
def create_chat_flow(chatStateFlow: ChatStateFlow) -> Dict:
    chatStateFlow = chatStateFlowServices.createChatFlow(chatStateFlow)
    return chatStateFlow

@chatStateRouter.get("/chatState/game/{gameName}")
def get_chat_flows(gameName: str) -> List[Dict]:
    chatStateFlows = chatStateFlowServices.listChatFlows(gameName)
    return chatStateFlows


@chatStateRouter.get("/chatState/{chatFlowId}")
def get_chat_flow(chatFlowId: str) -> Dict:
    chatStateFlow = chatStateFlowServices.getChatFlow(chatFlowId)
    return chatStateFlow

@chatStateRouter.patch("/chatState/update/{chatFlowId}")
def update_chat_flow(chatFlowId: str, chatStateFlow: ChatStateFlow) -> Dict:
    return chatStateFlowServices.updateChatFlow(chatFlowId, chatStateFlow)

@chatStateRouter.delete("/chatState/delete/{chatFlowId}")
def delete_chat_flow(chatFlowId: str) -> Dict:
    chatStateFlow = chatStateFlowServices.deleteChatFlow(chatFlowId)
    return chatStateFlow