from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import Optional

from services.persona_generator import PersonaGenerator
from services.interview_conductor import InterviewConductor
from services.requirements_document_generator import (
    RequirementsDocumentGenerator,
)
from services.information_evaluator import InformationEvaluator
from models.interview import InterviewState, InterviewResult


class DocumentationAgent:
    def __init__(self, llm: ChatOpenAI, k: Optional[int] = None):
        self.persona_generator = PersonaGenerator(llm, k=5)
        self.interview_generator = InterviewConductor(llm)
        self.information_evaluator = InformationEvaluator(llm)
        self.requirements_document_generator = RequirementsDocumentGenerator(llm)

        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(InterviewState)

        workflow.add_node("generate_personas", self._generate_personas)
        workflow.add_node("conduct_interviews", self._conduct_interviews)
        workflow.add_node("evaluate_information", self._evaluate_information)
        workflow.add_node("generate_requirements", self._generate_requirements)

        # これは workflow.add_edge(START, "agent") と同等
        workflow.set_entry_point("generate_personas")

        workflow.add_edge("generate_personas", "conduct_interviews")
        workflow.add_edge("conduct_interviews", "evaluate_information")

        workflow.add_conditional_edges(
            "evaluate_information",
            lambda state: not state.is_information_sufficient and state.iteration < 5,
            {True: "generate_personas", False: "generate_requirements"},
        )

        workflow.add_edge("generate_requirements", END)

        return workflow.compile()

    def _generate_personas(self, state: InterviewState) -> dict:
        new_personas = self.persona_generator.run(state.user_request)
        return {
            "personas": new_personas.personas,
            "iteration": state.iteration + 1,
        }

    def _conduct_interviews(self, state: InterviewState) -> dict:
        new_interviews: InterviewResult = self.interview_generator.run(
            state.user_request,
            state.personas,
        )
        return {"interviews": new_interviews.interviews}

    def _evaluate_information(self, state: InterviewState) -> dict:
        evaluation_result = self.information_evaluator.run(
            state.user_request,
            state.interviews,
        )
        return {
            "is_information_sufficient": evaluation_result.is_sufficient,
            "reason": evaluation_result.reason,
        }

    def _generate_requirements(self, state: InterviewState) -> dict:
        requirements_doc = self.requirements_document_generator.run(
            state.user_request,
            state.interviews,
        )
        return {"requirements_doc": requirements_doc}

    def run(self, user_request: str) -> str:
        initial_state = InterviewState(user_request=user_request)
        final_state = self.graph.invoke(initial_state)

        return final_state["requirements_doc"]
