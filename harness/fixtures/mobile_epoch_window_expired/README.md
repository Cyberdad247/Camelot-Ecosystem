# Fixture: mobile_epoch_window_expired

Phone attempts an offline device action (`device.sms.send` /
`device.call.initiate`) whose cached authority epoch exceeds the §10.3
window (5 min). The device must consult Sentinel before proceeding;
an offline action past the window is denied.

Verify: `mobile_epoch_window_enforced` fires; action denied offline;
device must phone home; receipt queued with `transport: pending` if any
(§10.3).
