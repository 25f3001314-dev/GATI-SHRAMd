"""Mock adapters for proposed mobility data sources.

Each class is deliberately small so a real API, CSV, database, or government
integration can replace only its fetch implementation later.
"""

from app.models.signals import RawRecord


class DemoAdapter:
    """Base implementation returning realistic, clearly synthetic demo data."""

    name = "demo"
    signal_type = "mobility_observation"
    district = "Gaya"
    origin = "Bihar"
    destination = "Maharashtra"
    base_volume = 120

    def fetch_records(self) -> list[RawRecord]:
        return [
            RawRecord(
                source=self.name,
                state="Bihar",
                district=self.district,
                origin=self.origin,
                destination=self.destination,
                timestamp="2026-01-08T10:30:00+00:00",
                signal_type=self.signal_type,
                volume=self.base_volume,
                worker_id=f"demo-{self.name.lower().replace('/', '-').replace(' ', '-')}-001",
                phone_number="+91-0000000000",
                aadhaar_like_id="DEMO-AADHAAR-0001",
                name="Synthetic Worker",
                email="demo@example.invalid",
                metadata={"synthetic": "true", "adapter": self.name},
            ),
            RawRecord(
                source=self.name,
                state="Bihar",
                district=self.district,
                origin=self.origin,
                destination="Delhi",
                timestamp="2026-01-15T14:00:00+00:00",
                signal_type=self.signal_type,
                volume=max(20, self.base_volume // 2),
                worker_id=f"demo-{self.name.lower().replace('/', '-').replace(' ', '-')}-002",
                phone_number="+91-0000000001",
                metadata={"synthetic": "true", "adapter": self.name},
            ),
        ]


class OnorcAdapter(DemoAdapter):
    name = "ONORC"


class IndianRailwaysUTSAdapter(DemoAdapter):
    name = "Indian Railways UTS"
    signal_type = "ticketing_volume"
    base_volume = 480


class EShramAdapter(DemoAdapter):
    name = "e-Shram"
    signal_type = "worker_registration_signal"
    base_volume = 90


class MGNREGAAdapter(DemoAdapter):
    name = "MGNREGA"
    signal_type = "work_demand_signal"
    base_volume = 150


class EPFOESICAdapter(DemoAdapter):
    name = "EPFO/ESIC"
    signal_type = "employment_transition"
    base_volume = 75


class BOCWAdapter(DemoAdapter):
    name = "BOCW"
    signal_type = "construction_worker_signal"
    base_volume = 110


class StateWorkerRegistryAdapter(DemoAdapter):
    name = "State Worker Registry"
    signal_type = "registry_movement_signal"
    base_volume = 130


class FASTagAdapter(DemoAdapter):
    name = "FASTag"
    signal_type = "road_mobility_volume"
    base_volume = 620


class EmployerContractorFeedAdapter(DemoAdapter):
    """Proposed zero-click employer/contractor ingestion boundary."""

    name = "Employer/Contractor feeds"
    signal_type = "labor_demand_signal"
    base_volume = 180


class WorkerOptInAdapter(DemoAdapter):
    """Voluntary missed-call / WhatsApp opt-in boundary."""

    name = "Worker voluntary opt-in"
    signal_type = "voluntary_intent_signal"
    base_volume = 40


DEMO_ADAPTERS: tuple[type[DemoAdapter], ...] = (
    OnorcAdapter,
    IndianRailwaysUTSAdapter,
    EShramAdapter,
    MGNREGAAdapter,
    EPFOESICAdapter,
    BOCWAdapter,
    StateWorkerRegistryAdapter,
    FASTagAdapter,
    EmployerContractorFeedAdapter,
    WorkerOptInAdapter,
)
