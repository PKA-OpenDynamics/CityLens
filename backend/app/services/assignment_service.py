# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Assignment Service - Business logic for report assignment system
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.assignment import (
    Department,
    ReportAssignment,
    AssignmentHistory,
    DepartmentMember,
    AssignmentStatus
)
from app.models.report import Report, ReportStatus


class AssignmentService:
    """Service for assignment business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_assignment(
        self,
        report_id: int,
        department_id: int,
        assigned_by: int,
        assigned_to: Optional[int] = None,
        priority: int = 3,
        notes: Optional[str] = None
    ) -> ReportAssignment:
        """
        Tạo phân công mới
        
        Args:
            report_id: ID báo cáo
            department_id: ID department
            assigned_by: ID người phân công
            assigned_to: ID người được giao cụ thể (optional)
            priority: Mức độ ưu tiên (1-4)
            notes: Ghi chú
        
        Returns:
            ReportAssignment object
        """
        # Get department for SLA
        department = self.db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise ValueError("Department not found")
        
        # Calculate deadlines
        now = datetime.utcnow()
        response_deadline = now + timedelta(hours=department.sla_response_hours)
        due_date = now + timedelta(hours=department.sla_resolution_hours)
        
        # Create assignment
        assignment = ReportAssignment(
            report_id=report_id,
            department_id=department_id,
            assigned_by=assigned_by,
            assigned_to=assigned_to,
            status=AssignmentStatus.ASSIGNED,
            due_date=due_date,
            response_deadline=response_deadline,
            priority=priority
        )
        
        if notes:
            assignment.notes = [{
                "timestamp": now.isoformat(),
                "user_id": assigned_by,
                "note": notes,
                "type": "created"
            }]
        
        self.db.add(assignment)
        
        # Update report status
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if report and report.status == ReportStatus.PENDING:
            report.status = ReportStatus.VERIFIED
        
        # Update department stats
        department.total_assigned += 1
        
        # Create history entry
        self._create_history(
            assignment_id=None,  # Will be set after commit
            user_id=assigned_by,
            action="created",
            description=f"Assignment created for department {department.name_vi}"
        )
        
        self.db.commit()
        self.db.refresh(assignment)
        
        # TODO: Send notification to department and assignee
        
        return assignment
    
    def accept_assignment(
        self,
        assignment_id: int,
        user_id: int,
        estimated_completion: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> ReportAssignment:
        """Department tiếp nhận phân công"""
        assignment = self.db.query(ReportAssignment).filter(
            ReportAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise ValueError("Assignment not found")
        
        if assignment.status != AssignmentStatus.ASSIGNED:
            raise ValueError(f"Cannot accept assignment in status {assignment.status}")
        
        # Verify user is member of department
        member = self.db.query(DepartmentMember).filter(
            and_(
                DepartmentMember.department_id == assignment.department_id,
                DepartmentMember.user_id == user_id,
                DepartmentMember.can_accept_assignments == True,
                DepartmentMember.is_active == True
            )
        ).first()
        
        if not member:
            raise ValueError("User not authorized to accept assignment for this department")
        
        now = datetime.utcnow()
        assignment.status = AssignmentStatus.ACCEPTED
        assignment.accepted_at = now
        assignment.accepted_by = user_id
        assignment.started_at = now
        assignment.estimated_completion = estimated_completion
        
        # Calculate response time
        assignment.response_time_hours = (now - assignment.assigned_at).total_seconds() / 3600
        
        # Add note
        if notes:
            current_notes = assignment.notes or []
            current_notes.append({
                "timestamp": now.isoformat(),
                "user_id": user_id,
                "note": notes,
                "type": "accepted"
            })
            assignment.notes = current_notes
        
        # Update report status
        report = self.db.query(Report).filter(Report.id == assignment.report_id).first()
        if report:
            report.status = ReportStatus.IN_PROGRESS
        
        self._create_history(
            assignment_id=assignment_id,
            user_id=user_id,
            action="accepted",
            description="Assignment accepted"
        )
        
        self.db.commit()
        self.db.refresh(assignment)
        
        return assignment
    
    def reject_assignment(
        self,
        assignment_id: int,
        user_id: int,
        rejection_reason: str
    ) -> ReportAssignment:
        """Department từ chối phân công"""
        assignment = self.db.query(ReportAssignment).filter(
            ReportAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise ValueError("Assignment not found")
        
        if assignment.status not in [AssignmentStatus.ASSIGNED, AssignmentStatus.ACCEPTED]:
            raise ValueError(f"Cannot reject assignment in status {assignment.status}")
        
        assignment.status = AssignmentStatus.REJECTED
        assignment.rejection_reason = rejection_reason
        
        # Add note
        current_notes = assignment.notes or []
        current_notes.append({
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "note": f"Rejected: {rejection_reason}",
            "type": "rejected"
        })
        assignment.notes = current_notes
        
        # Update report status back
        report = self.db.query(Report).filter(Report.id == assignment.report_id).first()
        if report:
            report.status = ReportStatus.VERIFIED  # Back to verified, needs reassignment
        
        self._create_history(
            assignment_id=assignment_id,
            user_id=user_id,
            action="rejected",
            description=f"Assignment rejected: {rejection_reason}"
        )
        
        self.db.commit()
        self.db.refresh(assignment)
        
        return assignment
    
    def complete_assignment(
        self,
        assignment_id: int,
        user_id: int,
        resolution_note: str,
        resolution_attachments: Optional[List[str]] = None
    ) -> ReportAssignment:
        """Hoàn thành phân công"""
        assignment = self.db.query(ReportAssignment).filter(
            ReportAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise ValueError("Assignment not found")
        
        if assignment.status not in [AssignmentStatus.ACCEPTED, AssignmentStatus.WORKING]:
            raise ValueError(f"Cannot complete assignment in status {assignment.status}")
        
        now = datetime.utcnow()
        assignment.status = AssignmentStatus.COMPLETED
        assignment.completed_at = now
        assignment.resolution_note = resolution_note
        assignment.resolution_attachments = resolution_attachments or []
        
        # Calculate resolution time
        assignment.resolution_time_hours = (now - assignment.assigned_at).total_seconds() / 3600
        
        # Add note
        current_notes = assignment.notes or []
        current_notes.append({
            "timestamp": now.isoformat(),
            "user_id": user_id,
            "note": "Assignment completed",
            "type": "completed"
        })
        assignment.notes = current_notes
        
        # Update report status
        report = self.db.query(Report).filter(Report.id == assignment.report_id).first()
        if report:
            report.status = ReportStatus.RESOLVED
            report.resolved_at = now
            report.resolution_note = resolution_note
        
        # Update department stats
        department = self.db.query(Department).filter(
            Department.id == assignment.department_id
        ).first()
        if department:
            department.total_resolved += 1
            
            # Recalculate avg metrics
            completed_assignments = self.db.query(ReportAssignment).filter(
                and_(
                    ReportAssignment.department_id == department.id,
                    ReportAssignment.status == AssignmentStatus.COMPLETED
                )
            ).all()
            
            if completed_assignments:
                avg_response = sum(a.response_time_hours for a in completed_assignments if a.response_time_hours) / len(completed_assignments)
                avg_resolution = sum(a.resolution_time_hours for a in completed_assignments if a.resolution_time_hours) / len(completed_assignments)
                
                department.avg_response_time_hours = avg_response
                department.avg_resolution_time_hours = avg_resolution
                department.resolution_rate = department.total_resolved / department.total_assigned
        
        self._create_history(
            assignment_id=assignment_id,
            user_id=user_id,
            action="completed",
            description="Assignment completed"
        )
        
        self.db.commit()
        self.db.refresh(assignment)
        
        return assignment
    
    def add_note(
        self,
        assignment_id: int,
        user_id: int,
        note: str,
        note_type: str = "update"
    ) -> ReportAssignment:
        """Thêm ghi chú vào assignment"""
        assignment = self.db.query(ReportAssignment).filter(
            ReportAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise ValueError("Assignment not found")
        
        current_notes = assignment.notes or []
        current_notes.append({
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "note": note,
            "type": note_type
        })
        assignment.notes = current_notes
        
        self.db.commit()
        self.db.refresh(assignment)
        
        return assignment
    
    def get_department_assignments(
        self,
        department_id: int,
        status: Optional[AssignmentStatus] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[ReportAssignment], int]:
        """Lấy danh sách phân công của department"""
        query = self.db.query(ReportAssignment).filter(
            ReportAssignment.department_id == department_id
        )
        
        if status:
            query = query.filter(ReportAssignment.status == status)
        
        total = query.count()
        
        assignments = query.order_by(
            ReportAssignment.priority.asc(),
            ReportAssignment.due_date.asc()
        ).offset(skip).limit(limit).all()
        
        return assignments, total
    
    def get_user_assignments(
        self,
        user_id: int,
        status: Optional[AssignmentStatus] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[ReportAssignment], int]:
        """Lấy danh sách phân công của user"""
        query = self.db.query(ReportAssignment).filter(
            ReportAssignment.assigned_to == user_id
        )
        
        if status:
            query = query.filter(ReportAssignment.status == status)
        
        total = query.count()
        
        assignments = query.order_by(
            ReportAssignment.priority.asc(),
            ReportAssignment.due_date.asc()
        ).offset(skip).limit(limit).all()
        
        return assignments, total
    
    def check_overdue_assignments(self):
        """Kiểm tra và đánh dấu assignments quá hạn"""
        now = datetime.utcnow()
        
        overdue = self.db.query(ReportAssignment).filter(
            and_(
                ReportAssignment.due_date < now,
                ReportAssignment.status.in_([
                    AssignmentStatus.ASSIGNED,
                    AssignmentStatus.ACCEPTED,
                    AssignmentStatus.WORKING
                ]),
                ReportAssignment.is_overdue == False
            )
        ).all()
        
        for assignment in overdue:
            assignment.is_overdue = True
        
        self.db.commit()
        
        return len(overdue)
    
    def get_department_stats(self, department_id: int) -> Dict[str, Any]:
        """Thống kê performance của department"""
        department = self.db.query(Department).filter(
            Department.id == department_id
        ).first()
        
        if not department:
            raise ValueError("Department not found")
        
        total_assigned = department.total_assigned
        total_completed = department.total_resolved
        
        pending = self.db.query(ReportAssignment).filter(
            and_(
                ReportAssignment.department_id == department_id,
                ReportAssignment.status.in_([
                    AssignmentStatus.ASSIGNED,
                    AssignmentStatus.ACCEPTED,
                    AssignmentStatus.WORKING
                ])
            )
        ).count()
        
        overdue = self.db.query(ReportAssignment).filter(
            and_(
                ReportAssignment.department_id == department_id,
                ReportAssignment.is_overdue == True,
                ReportAssignment.status != AssignmentStatus.COMPLETED
            )
        ).count()
        
        # SLA compliance rate
        completed = self.db.query(ReportAssignment).filter(
            and_(
                ReportAssignment.department_id == department_id,
                ReportAssignment.status == AssignmentStatus.COMPLETED
            )
        ).all()
        
        sla_compliant = sum(1 for a in completed if a.resolution_time_hours <= department.sla_resolution_hours)
        sla_compliance_rate = sla_compliant / len(completed) if completed else 0.0
        
        return {
            "department_id": department_id,
            "department_name": department.name_vi,
            "total_assigned": total_assigned,
            "total_completed": total_completed,
            "total_pending": pending,
            "total_overdue": overdue,
            "avg_response_time_hours": department.avg_response_time_hours,
            "avg_resolution_time_hours": department.avg_resolution_time_hours,
            "resolution_rate": department.resolution_rate,
            "sla_compliance_rate": sla_compliance_rate
        }
    
    def auto_assign_report(self, report_id: int, assigned_by: int) -> Optional[ReportAssignment]:
        """
        Tự động phân công báo cáo dựa trên category và district
        
        Args:
            report_id: ID báo cáo
            assigned_by: ID người tạo assignment (system)
        
        Returns:
            ReportAssignment nếu tìm được department phù hợp, None nếu không
        """
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return None
        
        # Find departments that handle this category
        departments = self.db.query(Department).filter(
            and_(
                Department.categories.contains([report.category]),
                Department.is_active == True
            )
        ).all()
        
        # Filter by district if report has district_id
        if report.district_id and departments:
            departments = [d for d in departments if not d.districts or report.district_id in d.districts]
        
        if not departments:
            return None
        
        # Select department with lowest current workload
        best_department = min(departments, key=lambda d: d.total_assigned - d.total_resolved)
        
        # Create assignment
        return self.create_assignment(
            report_id=report_id,
            department_id=best_department.id,
            assigned_by=assigned_by,
            notes="Auto-assigned based on category and location"
        )
    
    def _create_history(
        self,
        assignment_id: Optional[int],
        user_id: Optional[int],
        action: str,
        description: str
    ):
        """Create history entry"""
        if assignment_id:
            history = AssignmentHistory(
                assignment_id=assignment_id,
                user_id=user_id,
                action=action,
                description=description
            )
            self.db.add(history)
