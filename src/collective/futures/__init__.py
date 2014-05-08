from collective.futures.api import (
    result,
    submit,
    submitMultiprocess,
    resultOrSubmit,
    resultOrSubmitMultiprocess,
    cancel,
    clear,
    reset
)
from collective.futures.exceptions import (
    FuturesException,
    FutureNotSubmittedError,
    FutureNotResolvedError,
    FutureAlreadyResolvedError
)