# Converter Post-Layout Temporary Submission Proof

This page is generated from the temporary submission proof artifact.

The proof checks the final mechanical path without creating canonical accepted evidence. It builds a complete temporary candidate package, previews submission, runs the strict submitter into a temporary accepted directory, and verifies that the temporary accepted files are removed with the temporary workspace.

## First Principle

The submitter has to satisfy two opposite requirements.

It must be able to write accepted evidence when the payload is complete. Otherwise the project can only reject evidence and can never accept a real run.

It must not write accepted evidence during tests. Otherwise a temporary fixture can be mistaken for hardware evidence.

This proof checks both facts at once. The write path works, and the canonical accepted-evidence directory stays absent.

## Refused Claim

This proof does not create canonical accepted evidence, does not prove the temporary files are real layout or silicon, and does not upgrade the converter claim.
