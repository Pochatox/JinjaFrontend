class ConnectionError(Exception): ...


AuthorizationHeaderMissing = "miss-1"
RefreshTokenHeaderMissing = "miss-2"

RegistrationTokenInvalid = "inv-1"
AccessTokenInvalid = "inv-2"
RefreshTokenInvalid = "inv-3"
ChangePasswordTokenInvalid = "inv-4"

UsernameNotUnique = "uniq-1"
EmailNotUnique = "uniq-2"

EmailNonExists = "exist-1"
UserNotExists = "exist-3"

AccessTokenExpired = "exp-1"
RefreshTokenExpired = "exp-2"

UserIsActive = "other-1"
InvalidCredentials = "other-2"
TokensSubjectNotEqual = "other-4"
