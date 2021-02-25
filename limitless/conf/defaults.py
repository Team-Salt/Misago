# pylint: disable=line-too-long
"""
Default LimitLess settings. Override these with settings in the module pointed to
by the DJANGO_SETTINGS_MODULE environment variable.

If you rely on any of those in your code, make sure you use `limitless.conf.settings`
instead of Django's `django.conf.settings`.
"""

# Permissions system extensions
# https://limitless.readthedocs.io/en/latest/developers/acls.html#extending-permissions-system

LIMITLESS_ACL_EXTENSIONS = [
    "limitless.users.permissions.account",
    "limitless.users.permissions.profiles",
    "limitless.users.permissions.moderation",
    "limitless.users.permissions.delete",
    "limitless.categories.permissions",
    "limitless.threads.permissions.attachments",
    "limitless.threads.permissions.polls",
    "limitless.threads.permissions.threads",
    "limitless.threads.permissions.privatethreads",
    "limitless.threads.permissions.bestanswers",
    "limitless.search.permissions",
]


# Path to the directory that LimitLess should use to prepare user data downloads.
# Should not be accessible from internet.

LIMITLESS_USER_DATA_DOWNLOADS_WORKING_DIR = None


# Custom markup extensions

LIMITLESS_MARKUP_EXTENSIONS = []


# Bleach callbacks for linkifying paragraphs

LIMITLESS_BLEACH_CALLBACKS = []


# Custom post validators

LIMITLESS_POST_VALIDATORS = []


# Post search filters

LIMITLESS_POST_SEARCH_FILTERS = []


# Posting middlewares
# https://limitless.readthedocs.io/en/latest/developers/posting_process.html

LIMITLESS_POSTING_MIDDLEWARES = [
    # Always keep FloodProtectionMiddleware middleware first one
    "limitless.threads.api.postingendpoint.floodprotection.FloodProtectionMiddleware",
    "limitless.threads.api.postingendpoint.category.CategoryMiddleware",
    "limitless.threads.api.postingendpoint.privatethread.PrivateThreadMiddleware",
    "limitless.threads.api.postingendpoint.reply.ReplyMiddleware",
    "limitless.threads.api.postingendpoint.moderationqueue.ModerationQueueMiddleware",
    "limitless.threads.api.postingendpoint.attachments.AttachmentsMiddleware",
    "limitless.threads.api.postingendpoint.participants.ParticipantsMiddleware",
    "limitless.threads.api.postingendpoint.pin.PinMiddleware",
    "limitless.threads.api.postingendpoint.close.CloseMiddleware",
    "limitless.threads.api.postingendpoint.hide.HideMiddleware",
    "limitless.threads.api.postingendpoint.protect.ProtectMiddleware",
    "limitless.threads.api.postingendpoint.recordedit.RecordEditMiddleware",
    "limitless.threads.api.postingendpoint.updatestats.UpdateStatsMiddleware",
    "limitless.threads.api.postingendpoint.mentions.MentionsMiddleware",
    "limitless.threads.api.postingendpoint.subscribe.SubscribeMiddleware",
    "limitless.threads.api.postingendpoint.syncprivatethreads.SyncPrivateThreadsMiddleware",
    # Always keep SaveChangesMiddleware middleware after all state-changing middlewares
    "limitless.threads.api.postingendpoint.savechanges.SaveChangesMiddleware",
    # Those middlewares are last because they don't change app state
    "limitless.threads.api.postingendpoint.emailnotification.EmailNotificationMiddleware",
]


# Configured thread types

LIMITLESS_THREAD_TYPES = [
    "limitless.threads.threadtypes.thread.Thread",
    "limitless.threads.threadtypes.privatethread.PrivateThread",
]


# Search extensions

LIMITLESS_SEARCH_EXTENSIONS = [
    "limitless.threads.search.SearchThreads",
    "limitless.users.search.SearchUsers",
]


# Additional registration validators
# https://limitless.readthedocs.io/en/latest/developers/validating_registrations.html

LIMITLESS_NEW_REGISTRATIONS_VALIDATORS = [
    "limitless.users.validators.validate_gmail_email",
    "limitless.users.validators.validate_with_sfs",
]


# Custom profile fields

LIMITLESS_PROFILE_FIELDS = []


# Login API URL

LIMITLESS_LOGIN_API_URL = "auth"


# LimitLess Admin Path
# Omit starting and trailing slashes. To disable LimitLess admin, empty this value.

LIMITLESS_ADMIN_PATH = "admincp"


# Admin urls namespaces that LimitLess's AdminAuthMiddleware should protect

LIMITLESS_ADMIN_NAMESPACES = ["admin", "limitless:admin"]


# How long (in minutes) since previous request to admin namespace should admin session last.

LIMITLESS_ADMIN_SESSION_EXPIRATION = 60


# Display threads on forum index
# Change this to false to display categories list instead

LIMITLESS_THREADS_ON_INDEX = True


# Function used for generating individual avatar for user

LIMITLESS_DYNAMIC_AVATAR_DRAWER = "limitless.users.avatars.dynamic.draw_default"


# Path to directory containing avatar galleries
# Those galleries can be loaded by running loadavatargallery command

LIMITLESS_AVATAR_GALLERY = None


# Save user avatars for sizes
# Keep sizes ordered from greatest to smallest
# Max size also controls min size of uploaded image as well as crop size

LIMITLESS_AVATARS_SIZES = [400, 200, 150, 100, 64, 50, 30]


# Path to blank avatar image used for guests and removed users.

LIMITLESS_BLANK_AVATAR = "limitless/img/blank-avatar.png"


# Max allowed size of image before LimitLess will generate thumbnail for it

LIMITLESS_ATTACHMENT_IMAGE_SIZE_LIMIT = (500, 500)


# Length of secret used for attachments url tokens and filenames

LIMITLESS_ATTACHMENT_SECRET_LENGTH = 64


# Names of files served when user requests file that doesn't exist or is unavailable

LIMITLESS_ATTACHMENT_403_IMAGE = "limitless/img/attachment-403.png"
LIMITLESS_ATTACHMENT_404_IMAGE = "limitless/img/attachment-404.png"


# Available Moment.js locales

LIMITLESS_MOMENT_JS_LOCALES = [
    "af",
    "ar-ma",
    "ar-sa",
    "ar-tn",
    "ar",
    "az",
    "be",
    "bg",
    "bn",
    "bo",
    "br",
    "bs",
    "ca",
    "cs",
    "cv",
    "cy",
    "da",
    "de-at",
    "de",
    "el",
    "en-au",
    "en-ca",
    "en-gb",
    "eo",
    "es",
    "et",
    "eu",
    "fa",
    "fi",
    "fo",
    "fr-ca",
    "fr",
    "fy",
    "gl",
    "he",
    "hi",
    "hr",
    "hu",
    "hy-am",
    "id",
    "is",
    "it",
    "ja",
    "ka",
    "km",
    "ko",
    "lb",
    "lt",
    "lv",
    "mk",
    "ml",
    "mr",
    "ms-my",
    "my",
    "nb",
    "ne",
    "nl",
    "nn",
    "pl",
    "pt-br",
    "pt",
    "ro",
    "ru",
    "sk",
    "sl",
    "sq",
    "sr-cyrl",
    "sr",
    "sv",
    "ta",
    "th",
    "tl-ph",
    "tr",
    "tzm-latn",
    "tzm",
    "uk",
    "uz",
    "vi",
    "zh-cn",
    "zh-hans",
    "zh-tw",
]
