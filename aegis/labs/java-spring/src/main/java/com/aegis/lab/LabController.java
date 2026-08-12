package com.aegis.lab;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class LabController {

    @GetMapping("/")
    public Map<String, String> root() {

        return Map.of(
            "name",
            "Aegis Java Spring Lab",

            "endpoint",
            "/search"
        );
    }

    @GetMapping("/health")
    public Map<String, String> health() {

        return Map.of(
            "status",
            "ok"
        );
    }

    @GetMapping("/search")
    public Map<String, String> search(
        @RequestParam(
            defaultValue = ""
        )
        String q
    ) {

        // Intentionally reflects
        // user-controlled input.

        return Map.of(
            "query",
            q
        );
    }
}