"""HTTP endpoints for the email OTP module. Wired into server.py with build_router()."""
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from . import otp


class VerifyIn(BaseModel):
    challenge: str
    code: str


class ResendIn(BaseModel):
    challenge: str


class ContactIn(BaseModel):
    reg_no: str
    email: str


class FillIn(BaseModel):
    base_email: str


def _call(fn, *args):
    try:
        return fn(*args)
    except otp.OtpError as exc:
        raise HTTPException(exc.status, exc.message)


def build_router(require_admin: Callable, finish_login: Callable[[int, str], dict], roster: Callable[[int], list[str]]) -> APIRouter:
    """finish_login(election_id, reg_no) issues the real voter session once the code is right;
    roster(election_id) lists the registration numbers on that election."""
    otp.init()
    r = APIRouter()

    @r.post('/api/voter/otp/verify')
    def verify(body: VerifyIn):
        election_id, reg_no = _call(otp.verify, body.challenge, body.code)
        return finish_login(election_id, reg_no)

    @r.post('/api/voter/otp/resend')
    def resend(body: ResendIn):
        return _call(otp.resend, body.challenge)

    @r.get('/api/admin/otp/status')
    def status(_=Depends(require_admin)):
        return otp.status()

    @r.get('/api/admin/otp/outbox')
    def outbox(_=Depends(require_admin)):
        return otp.outbox()

    @r.get('/api/admin/elections/{e_id}/contacts')
    def get_contacts(e_id: int, _=Depends(require_admin)):
        return otp.contacts(e_id)

    @r.put('/api/admin/elections/{e_id}/contacts')
    def put_contact(e_id: int, body: ContactIn, _=Depends(require_admin)):
        if body.reg_no.strip().upper() not in set(roster(e_id)):
            raise HTTPException(404, "That registration number isn't on this election's roster.")
        _call(otp.set_contact, e_id, body.reg_no, body.email)
        return {'ok': True}

    @r.post('/api/admin/elections/{e_id}/contacts/fill')
    def fill(e_id: int, body: FillIn, _=Depends(require_admin)):
        return {'filled': _call(otp.fill_plus_addresses, e_id, roster(e_id), body.base_email)}

    return r
