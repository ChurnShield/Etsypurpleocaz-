"""
crew.py — PurpleOcaz Listing Crew (Phase 1: Planner + Builder).
"""

import os
from pathlib import Path

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from crewai_crew.tools.factory_tool import run_template_factory, run_hero_pipeline
from crewai_crew.tools.verify_tool import (
    run_evaluate,
    run_verify,
    read_file,
    write_file,
    write_sprint_contract,
)

# ── LLM ──────────────────────────────────────────────────────────────────────
# Both agents use Claude Sonnet 4.6 via the ANTHROPIC_API_KEY in .env
_llm = LLM(
    model="anthropic/claude-sonnet-4-6",
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    temperature=0.2,         # low temp for structured JSON output
    max_tokens=8192,
)


@CrewBase
class PurpleOcazCrew:
    """Two-agent crew: Planner designs the niche, Builder executes it."""

    agents_config  = "config/agents.yaml"
    tasks_config   = "config/tasks.yaml"

    # ── Agents ────────────────────────────────────────────────────────────────

    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config["planner"],  # type: ignore[index]
            tools=[read_file, write_file],
            llm=_llm,
            verbose=True,
        )

    @agent
    def builder(self) -> Agent:
        return Agent(
            config=self.agents_config["builder"],  # type: ignore[index]
            tools=[
                run_template_factory,
                run_hero_pipeline,
                run_verify,
                run_evaluate,
                write_sprint_contract,
            ],
            llm=_llm,
            verbose=True,
        )

    # ── Tasks ─────────────────────────────────────────────────────────────────

    @task
    def plan_niche(self) -> Task:
        return Task(config=self.tasks_config["plan_niche"])  # type: ignore[index]

    @task
    def build_listing(self) -> Task:
        return Task(config=self.tasks_config["build_listing"])  # type: ignore[index]

    # ── Crew ──────────────────────────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
