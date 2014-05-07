from collective.futures.api import (
    result,
    submit,
    submitMultiprocess,
    resultOrSubmit,
    resultOrSubmitMultiprocess
)
from collective.futures.exceptions import (
    FuturesException,
    FutureNotSubmittedError,
    FutureNotResolvedError
)