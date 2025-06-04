# Thời gian token bị blacklist giữ lại (phút)
from datetime import timedelta

BLACKLIST_TOKEN_EXPIRE_MINUTES = 30

# Thời gian giữ log request (rate limiting)
TOKEN_USAGE_LOG_EXPIRE_MINUTES = 1

# Số lượng Request tối đa trong thời gian là (giây)
RATE_LIMIT_MAX_REQUESTS = 10
RATE_LIMIT_PERIOD_SECONDS = 10

# Được dùng để xác định login có đáng ngờ không
SUSPICIOUS_LOGIN_TIME_WINDOW = timedelta(minutes=2)

# Được dùng để xác định refresh token có đáng ngờ không
SUSPICIOUS_REFRESH_TIME_WINDOW = timedelta(seconds=10)