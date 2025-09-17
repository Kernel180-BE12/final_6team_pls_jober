package com.example.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.lang.NonNull;
import lombok.RequiredArgsConstructor;
import com.example.service.TokenService;
import com.example.entity.Account;
import com.example.repository.AccountRepository;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;

@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtTokenProvider jwtTokenProvider;
    private final TokenService tokenService;
    private final AccountRepository accountRepository;

    @Override
    protected void doFilterInternal(@NonNull HttpServletRequest request, @NonNull HttpServletResponse response, 
                                  @NonNull FilterChain filterChain) throws ServletException, IOException {
        
        String token = extractTokenFromRequest(request);
        
        if (token != null && jwtTokenProvider.validateToken(token)) {
            // 토큰 타입 확인 (Access Token만 허용)
            String tokenType = jwtTokenProvider.getTokenType(token);
            if ("access".equals(tokenType)) {
                // 블랙리스트 확인
                if (!tokenService.isTokenBlacklisted(token)) {
                    // JWT에서 accountId 추출
                    Long accountId = jwtTokenProvider.getAccountId(token);

                    if (accountId != null) {
                        // DB에서 실제 Account 엔티티 조회 (상태 확인)
                        Account account = accountRepository.findById(accountId).orElse(null);

                        if (account != null && "ACTIVE".equals(account.getStatus())) {
                            // Account 엔티티를 SecurityContext에 설정
                            UsernamePasswordAuthenticationToken auth =
                                new UsernamePasswordAuthenticationToken(
                                    account, // principal을 Account 엔티티로 설정
                                    null,
                                    Collections.singletonList(new SimpleGrantedAuthority(account.getRole()))
                                );
                            SecurityContextHolder.getContext().setAuthentication(auth);
                        }
                    }
                }
            }
        }
        
        filterChain.doFilter(request, response);
    }

    private String extractTokenFromRequest(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
