"""
Upload + analysis + history routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.rate_limit import limiter
from app.models.analysis import Analysis, VerdictLabel
from app.models.user import User
from app.schemas.analysis import AnalysisListItem, AnalysisOut, DashboardStats
from app.services.analysis_service import run_full_analysis
from app.services.logging_service import log_event
from app.services.pdf_report_service import generate_report_pdf
from app.services.storage import get_upload_path, save_upload, validate_upload
import io

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/upload", response_model=AnalysisOut, status_code=201)
@limiter.limit("10/minute")
async def upload_and_analyze(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = await file.read()
    validate_upload(file, content)
    stored_filename, abs_path, file_hash = save_upload(file, content)

    try:
        analysis = run_full_analysis(
            db=db,
            owner_id=current_user.id,
            stored_filename=stored_filename,
            original_filename=file.filename or stored_filename,
            file_size_bytes=len(content),
            file_hash=file_hash,
            abs_path=abs_path,
            image_bytes=content,
        )
    except Exception as exc:
        log_event(db, "ERROR", f"Analysis failed for upload by {current_user.email}: {exc}",
                  user_id=current_user.id)
        raise HTTPException(status_code=422, detail=f"Could not analyze image: {exc}")

    log_event(db, "ANALYSIS", f"{current_user.email} analyzed '{file.filename}' -> "
                                f"{analysis.verdict.value} ({analysis.confidence_score}%)",
              user_id=current_user.id, ip_address=request.client.host if request.client else None)
    return _to_analysis_out(analysis)


def _to_analysis_out(analysis: Analysis) -> AnalysisOut:
    from app.schemas.analysis import OCRFields
    return AnalysisOut(
        id=analysis.id,
        original_filename=analysis.original_filename,
        stored_filename=analysis.stored_filename,
        file_size_bytes=analysis.file_size_bytes,
        ocr=OCRFields(
            amount=analysis.ocr_amount, date=analysis.ocr_date, time=analysis.ocr_time,
            utr=analysis.ocr_utr, bank_name=analysis.ocr_bank_name,
            sender_upi=analysis.ocr_sender_upi, receiver_upi=analysis.ocr_receiver_upi,
            payment_status=analysis.ocr_payment_status, raw_text=analysis.ocr_raw_text,
        ),
        forensic_findings=analysis.forensic_findings or [],
        forensic_flags_count=analysis.forensic_flags_count,
        confidence_score=analysis.confidence_score,
        verdict=analysis.verdict.value,
        is_suspicious=analysis.is_suspicious,
        explanation_reasons=analysis.explanation_reasons or [],
        created_at=analysis.created_at,
    )


@router.get("/history", response_model=list[AnalysisListItem])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: str | None = Query(None, description="Search filename or UTR"),
    verdict: str | None = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|confidence_score)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
):
    q = db.query(Analysis).filter(Analysis.owner_id == current_user.id)
    if search:
        like = f"%{search}%"
        q = q.filter((Analysis.original_filename.ilike(like)) | (Analysis.ocr_utr.ilike(like)))
    if verdict:
        q = q.filter(Analysis.verdict == verdict)
    sort_col = Analysis.created_at if sort_by == "created_at" else Analysis.confidence_score
    q = q.order_by(sort_col.desc() if order == "desc" else sort_col.asc())
    return q.all()


@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.owner_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return _to_analysis_out(analysis)


@router.delete("/{analysis_id}", status_code=204)
def delete_analysis(analysis_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.owner_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    db.delete(analysis)
    db.commit()
    return None


@router.get("/{analysis_id}/image")
def get_analysis_image(analysis_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.owner_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    path = get_upload_path(analysis.stored_filename)
    return FileResponse(path)


@router.get("/{analysis_id}/report.pdf")
def download_report(analysis_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.owner_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    path = get_upload_path(analysis.stored_filename)
    pdf_bytes = generate_report_pdf(analysis, path)
    filename = f"forensic-report-{analysis.id}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/stats/dashboard", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    base_q = db.query(Analysis).filter(Analysis.owner_id == current_user.id)
    total = base_q.count()
    suspicious = base_q.filter(Analysis.verdict == VerdictLabel.HIGHLY_SUSPICIOUS).count()
    genuine = base_q.filter(Analysis.verdict == VerdictLabel.LIKELY_GENUINE).count()
    needs_review = base_q.filter(Analysis.verdict == VerdictLabel.NEEDS_REVIEW).count()
    avg_conf = db.query(func.avg(Analysis.confidence_score)).filter(Analysis.owner_id == current_user.id).scalar()

    timeline_rows = (
        db.query(func.date(Analysis.created_at).label("day"), func.count(Analysis.id))
        .filter(Analysis.owner_id == current_user.id)
        .group_by("day").order_by("day").all()
    )
    daily_timeline = [{"date": str(day), "count": count} for day, count in timeline_rows]

    return DashboardStats(
        total_analyses=total,
        suspicious_count=suspicious,
        genuine_count=genuine,
        needs_review_count=needs_review,
        average_confidence=round(float(avg_conf), 1) if avg_conf else 0.0,
        verdict_breakdown={
            "Likely Genuine": genuine,
            "Needs Manual Review": needs_review,
            "Highly Suspicious": suspicious,
        },
        daily_timeline=daily_timeline,
    )