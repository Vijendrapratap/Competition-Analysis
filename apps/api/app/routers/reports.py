from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import AccountId
from app.models.brands import BrandProfile
from app.models.analytics import Report
from app.schemas.analytics import ReportResponse
from app.services.pdf_report import generate_pdf

router = APIRouter()


@router.get("/brands/{brand_id}/reports", response_model=list[ReportResponse])
async def list_reports(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Report)
        .join(BrandProfile, Report.brand_profile_id == BrandProfile.id)
        .where(BrandProfile.id == brand_id, BrandProfile.account_id == account_id)
        .order_by(desc(Report.generated_at))
        .limit(20)
    )
    result = await db.execute(stmt)
    return [ReportResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Report)
        .join(BrandProfile, Report.brand_profile_id == BrandProfile.id)
        .where(Report.id == report_id, BrandProfile.account_id == account_id)
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportResponse.model_validate(report)


@router.get("/reports/{report_id}/pdf")
async def download_report_pdf(
    report_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Report)
        .join(BrandProfile, Report.brand_profile_id == BrandProfile.id)
        .where(Report.id == report_id, BrandProfile.account_id == account_id)
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.report_data:
        raise HTTPException(status_code=422, detail="Report has no data to export")

    # Get brand name
    stmt = select(BrandProfile.name).where(BrandProfile.id == report.brand_profile_id)
    result = await db.execute(stmt)
    brand_name = result.scalar_one_or_none() or "CompeteIQ"

    pdf_bytes = generate_pdf(report.report_data, brand_name)

    filename = f"competeiq-report-{report.filter_mode}-{report.period_start.strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/brands/{brand_id}/reports/latest/pdf")
async def download_latest_report_pdf(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    """Download the most recent report as PDF — used by the dashboard export button."""
    stmt = (
        select(Report)
        .join(BrandProfile, Report.brand_profile_id == BrandProfile.id)
        .where(BrandProfile.id == brand_id, BrandProfile.account_id == account_id)
        .order_by(desc(Report.generated_at))
        .limit(1)
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="No reports available. Run a collection first.")

    if not report.report_data:
        raise HTTPException(status_code=422, detail="Report has no data to export")

    stmt = select(BrandProfile.name).where(BrandProfile.id == report.brand_profile_id)
    result = await db.execute(stmt)
    brand_name = result.scalar_one_or_none() or "CompeteIQ"

    pdf_bytes = generate_pdf(report.report_data, brand_name)

    filename = f"competeiq-report-{report.filter_mode}-{report.period_start.strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
