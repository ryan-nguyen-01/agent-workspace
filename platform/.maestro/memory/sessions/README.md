# Session Memory

This directory contains short-lived conversation context. A long conversation must checkpoint durable
facts, resolved questions, progress, and the next action into task memory before a new conversation starts.

Session memory is local runtime data. Do not use it as the only source for a decision or completed work.
