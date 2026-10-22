"""Legacy demo password reset is intentionally disabled."""


def main() -> None:
    raise SystemExit(
        "Bulk password resetting is disabled for security. "
        "Use RenewGrid's authenticated change-password flow "
        "or the verified password-recovery process."
    )


if __name__ == "__main__":
    main()
