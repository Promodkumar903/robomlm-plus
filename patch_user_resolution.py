from pathlib import Path

p = Path(r"app\users\user_service.py")
s = p.read_text(encoding="utf-8")

if "class UserResolutionRules" in s:
    print("USER RESOLUTION: ALREADY PRESENT")
    raise SystemExit(0)

marker = """# ============================================================================
# USER REQUIREMENTS
# ============================================================================"""

if marker not in s:
    raise SystemExit("USER REQUIREMENTS MARKER NOT FOUND")

block = """
# ============================================================================
# USER RESOLUTION
# ============================================================================

class UserResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


class UserDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass
class UserResolutionRules:
    allow_when_ready: bool = True
    allow_when_conditionally_ready: bool = True
    review_when_not_ready: bool = True
    block_when_invalid: bool = True
    block_when_disabled: bool = True
    block_when_deleted: bool = True
    block_when_suspended: bool = True
    block_when_authority_violation: bool = True
    minimum_quality: float = 0.70
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserPresentation:
    user_id: str = ""
    display_name: str = ""
    email: str = ""
    status: UserStatus = UserStatus.UNKNOWN
    mode: UserMode = UserMode.UNKNOWN
    readiness: str = "NOT_READY"
    decision: UserDecision = UserDecision.UNKNOWN
    quality_score: float = 0.0
    flags: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserResult:
    request: Optional[UserRequest] = None
    reference: Optional[UserReference] = None
    user: Optional[UserRecord] = None
    assessment: Optional[UserAssessment] = None
    presentation: Optional[UserPresentation] = None
    decision: UserDecision = UserDecision.UNKNOWN
    resolution: UserResolutionStatus = UserResolutionStatus.REVIEW_REQUIRED
    flags: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    authority_valid: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


def collect_user_restrictions(
    user: Optional[UserRecord],
    assessment: Optional[UserAssessment] = None,
) -> List[str]:

    restrictions: List[str] = []

    if user is None:
        return ["USER_UNAVAILABLE"]

    if user.status == UserStatus.SUSPENDED:
        restrictions.append("USER_SUSPENDED")
    elif user.status == UserStatus.DISABLED:
        restrictions.append("USER_DISABLED")
    elif user.status == UserStatus.DELETED:
        restrictions.append("USER_DELETED")
    elif user.status == UserStatus.PENDING:
        restrictions.append("USER_PENDING")

    if assessment is not None:
        if assessment.readiness == "BLOCKED":
            restrictions.append("USER_NOT_ELIGIBLE")
        elif assessment.readiness == "NOT_READY":
            restrictions.append("USER_NOT_READY")
        elif assessment.readiness == "CONDITIONALLY_READY":
            restrictions.append("USER_CONDITIONAL")

    return sorted(set(restrictions))


def collect_user_flags(
    user: Optional[UserRecord],
    assessment: Optional[UserAssessment] = None,
) -> List[str]:

    flags: List[str] = []

    if user is None:
        return ["USER_MISSING"]

    if user.status == UserStatus.SUSPENDED:
        flags.append("USER_SUSPENDED")

    if user.status == UserStatus.PENDING:
        flags.append("USER_PENDING")

    if user.status == UserStatus.DISABLED:
        flags.append("USER_DISABLED")

    if user.status == UserStatus.DELETED:
        flags.append("USER_DELETED")

    if user.status == UserStatus.INVALID:
        flags.append("USER_INVALID")

    if assessment is not None:
        flags.extend(assessment.flags)

    return sorted(set(flags))


def build_user_presentation(
    user: Optional[UserRecord],
    assessment: Optional[UserAssessment],
    decision: UserDecision = UserDecision.UNKNOWN,
) -> UserPresentation:

    if user is None:
        return UserPresentation(
            decision=decision,
            readiness="BLOCKED",
            flags=["USER_MISSING"],
            restrictions=["USER_UNAVAILABLE"],
        )

    flags = collect_user_flags(user, assessment)
    restrictions = collect_user_restrictions(user, assessment)

    return UserPresentation(
        user_id=user.user_id,
        display_name=user.display_name,
        email=user.email,
        status=user.status,
        mode=user.mode,
        readiness=(
            assessment.readiness
            if assessment is not None
            else "NOT_READY"
        ),
        decision=decision,
        quality_score=(
            assessment.quality_score
            if assessment is not None
            else 0.0
        ),
        flags=flags,
        restrictions=restrictions,
        metadata={
            "engine": USER_SERVICE_ENGINE,
            "version": USER_SERVICE_VERSION,
            "user_domain": True,
            "authentication": False,
            "credential_verification": False,
            "billing": False,
            "subscription": False,
            "entitlement": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_mutation": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution": False,
            "upstream_mutation": False,
        },
    )


def resolve_user(
    request: UserRequest,
    user: Optional[UserRecord],
    requirements: Optional[UserRequirements] = None,
    rules: Optional[UserResolutionRules] = None,
) -> UserResult:

    rules = rules or UserResolutionRules()

    authority_check = validate_user_service_authority()
    authority_valid = bool(authority_check.valid)

    assessment: Optional[UserAssessment] = None

    if user is not None:
        assessment = assess_user(user, requirements)

    if not authority_valid and rules.block_when_authority_violation:
        decision = UserDecision.BLOCK
        resolution = UserResolutionStatus.BLOCKED

    elif user is None:
        decision = UserDecision.BLOCK
        resolution = UserResolutionStatus.BLOCKED

    elif user.status == UserStatus.INVALID and rules.block_when_invalid:
        decision = UserDecision.BLOCK
        resolution = UserResolutionStatus.BLOCKED

    elif user.status == UserStatus.DELETED and rules.block_when_deleted:
        decision = UserDecision.BLOCK
        resolution = UserResolutionStatus.BLOCKED

    elif user.status == UserStatus.DISABLED and rules.block_when_disabled:
        decision = UserDecision.BLOCK
        resolution = UserResolutionStatus.BLOCKED

    elif user.status == UserStatus.SUSPENDED and rules.block_when_suspended:
        decision = UserDecision.BLOCK
        resolution = UserResolutionStatus.BLOCKED

    elif assessment is None:
        decision = UserDecision.REVIEW_REQUIRED
        resolution = UserResolutionStatus.REVIEW_REQUIRED

    elif assessment.readiness == "BLOCKED":
        decision = UserDecision.BLOCK
        resolution = UserResolutionStatus.BLOCKED

    elif assessment.readiness == "NOT_READY":
        decision = UserDecision.REVIEW_REQUIRED
        resolution = UserResolutionStatus.REVIEW_REQUIRED

    elif assessment.readiness == "CONDITIONALLY_READY":

        if rules.allow_when_conditionally_ready:
            decision = UserDecision.ALLOW_WITH_RESTRICTION
            resolution = UserResolutionStatus.CONDITIONAL
        else:
            decision = UserDecision.REVIEW_REQUIRED
            resolution = UserResolutionStatus.REVIEW_REQUIRED

    elif assessment.quality_score < rules.minimum_quality:
        decision = UserDecision.REVIEW_REQUIRED
        resolution = UserResolutionStatus.REVIEW_REQUIRED

    elif not rules.allow_when_ready:
        decision = UserDecision.REVIEW_REQUIRED
        resolution = UserResolutionStatus.REVIEW_REQUIRED

    else:
        decision = UserDecision.ALLOW
        resolution = UserResolutionStatus.RESOLVED

    flags = collect_user_flags(user, assessment)
    restrictions = collect_user_restrictions(user, assessment)

    presentation = build_user_presentation(
        user=user,
        assessment=assessment,
        decision=decision,
    )

    reference = None

    if user is not None:
        try:
            reference = build_user_reference(user)
        except Exception:
            reference = None

    return UserResult(
        request=request,
        reference=reference,
        user=user,
        assessment=assessment,
        presentation=presentation,
        decision=decision,
        resolution=resolution,
        flags=flags,
        restrictions=restrictions,
        authority_valid=authority_valid,
        metadata={
            "engine": USER_SERVICE_ENGINE,
            "version": USER_SERVICE_VERSION,
            "resolution_layer": True,
            "authentication": False,
            "billing": False,
            "subscription": False,
            "entitlement": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_mutation": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution": False,
            "upstream_mutation": False,
        },
    )


def validate_user_result(
    result: UserResult,
) -> Dict[str, Any]:

    errors: List[str] = []

    if not isinstance(result, UserResult):
        return {
            "valid": False,
            "errors": ["RESULT_TYPE_INVALID"],
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    if result.user is not None:
        if not result.user.user_id:
            errors.append("USER_ID_MISSING")

    if result.assessment is not None:
        quality = result.assessment.quality_score

        if not isinstance(quality, (int, float)):
            errors.append("QUALITY_SCORE_INVALID")
        elif not 0.0 <= float(quality) <= 1.0:
            errors.append("QUALITY_SCORE_OUT_OF_RANGE")

    if not isinstance(result.authority_valid, bool):
        errors.append("AUTHORITY_VALID_INVALID")

    if not isinstance(result.flags, list):
        errors.append("FLAGS_INVALID")

    if not isinstance(result.restrictions, list):
        errors.append("RESTRICTIONS_INVALID")

    if not isinstance(result.metadata, dict):
        errors.append("METADATA_INVALID")

    return {
        "valid": not errors,
        "errors": errors,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


s = s.replace(marker, block + "\n\n" + marker, 1)

p.write_text(s, encoding="utf-8")

print("USER RESOLUTION BLOCK: INSERTED")